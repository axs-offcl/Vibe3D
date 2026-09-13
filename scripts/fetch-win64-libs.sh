#!/usr/bin/env bash
# Vibe3D — fetch the Blender win64_vc15 precompiled libs (r62700) that the
# STRIPPED build actually references, subtree by subtree.
#
# Why selective: with Cycles/OSL/OpenVDB/Alembic/USD/OpenCollada/XR disabled,
# ~6 GB of the 8 GB tree (llvm, osl, OpenImageDenoise, embree, usd, ...) is
# never referenced — and llvm/debug alone was where nearly every Cloudflare
# 429 landed (runs #13-#17).
#
# Why per-subtree + sentinel-gated: svn's exit code lies about completeness
# (run #16 "finished" at 3.4G/8G, then configure died on Python.h), and
# Cloudflare 429s cut long transfers mid-flight. A subtree is DONE only when
# its sentinel file exists on disk; interrupted subtrees are resumed with
# `svn cleanup` + `svn checkout --force` (re-entrant, verified locally).
#
# Usage: bash scripts/fetch-win64-libs.sh [lib-root]
#   lib-root defaults to ./lib (workflow: <repo>/lib, so lib/win64_vc15 is
#   created next to source/ exactly as Blender 2.83's CMake expects).

set -u

LIB_ROOT="${1:-lib}"
DEST="$LIB_ROOT/win64_vc15"
BASE="https://svn.blender.org/svnroot/bf-blender/trunk/lib/win64_vc15"
REV=62700

# Subtrees referenced by platform_win32.cmake / CMakeLists.txt defaults for
# the Vibe3D feature set (docs/STRIP_LIST.md). Keep in sync with the CMake
# flags in .github/workflows/build-vibe3d.yml.
# Fields: <svn path> <dest dir> <sentinel file>
# svn paths use the on-disk case at r62700; dest dirs match what cmake
# references (Windows paths are case-insensitive, but stay tidy).
SUBTREES=(
  "pthreads pthreads include/pthread.h"
  "zlib zlib include/zlib.h"
  "png png include/png.h"
  "jpeg jpeg include/jpeglib.h"
  "tiff tiff include/tiffio.h"
  "freetype freetype include/freetype2/ft2build.h"
  "iconv iconv include/iconv.h"
  # Big subtrees first: a burned runner IP only has ~20 MB of budget before
  # the 429 wall, a clean one can pull everything — ordering by size
  # descending maximizes completed subtrees per attempt.
  "boost boost include/boost/version.hpp"
  "python python/37 include/Python.h"
  "OpenImageIO OpenImageIO include/OpenImageIO/version.h"
  "ffmpeg ffmpeg include/libavcodec/avcodec.h"
  "openexr openexr include/OpenEXR/ImfVersion.h"
  "opencolorio OpenColorIO include/OpenColorIO/OpenColorABI.h"
  "opensubdiv opensubdiv include/opensubdiv/version.h"
  "tbb tbb include/tbb/tbb.h"
  "sdl sdl include/SDL.h"
  "openal openal include/AL/al.h"
  "sndfile sndfile include/sndfile.h"
  "fftw3 fftw3 include/fftw3.h"
  "openjpeg openjpeg include/openjpeg-2.3/openjpeg.h"
  "xr_openxr_sdk xr_openxr_sdk include/openxr/openxr.h"
  "pugixml pugixml include/pugixml.hpp"
  "wintab wintab include/wintab.h"
)

fetch_subtree() {
  local remote="$1" dest="$2" sentinel="$3"
  if [ -f "$DEST/$dest/$sentinel" ]; then
    echo "  OK (sentinel present): $remote"
    return 0
  fi
  mkdir -p "$DEST"
  svn cleanup "$DEST/$remote" >/dev/null 2>&1 || true
  local out=""
  if out=$(svn checkout -q --non-interactive -r "$REV" --force \
      "$BASE/$remote@$REV" "$DEST/$remote" 2>&1); then :; fi
  if [ -f "$DEST/$dest/$sentinel" ]; then
    echo "  done: $remote ($(du -sh "$DEST/$remote" 2>/dev/null | cut -f1))"
    return 0
  fi
  echo "  incomplete: $remote — $(echo "$out" | tail -1 | cut -c1-140)"
  return 1
}

main() {
  command -v svn >/dev/null 2>&1 || { echo "::error::svn not on PATH"; exit 1; }
  mkdir -p "$DEST"
  local failures=() item pass max_passes=6 zero_progress=0 prev_size next_size
  prev_size=$(du -sk "$DEST" 2>/dev/null | cut -f1); prev_size=${prev_size:-0}
  for pass in $(seq 1 $max_passes); do
    echo "=== pass $pass/$max_passes (tree so far: $((prev_size / 1024)) MB) ==="
    failures=()
    for item in "${SUBTREES[@]}"; do
      set -- $item
      fetch_subtree "$1" "$2" "$3" || failures+=("$1")
    done
    if [ ${#failures[@]} -eq 0 ]; then
      echo "ALL SUBTREES COMPLETE ($(du -sh "$DEST" | cut -f1))"
      exit 0
    fi
    next_size=$(du -sk "$DEST" 2>/dev/null | cut -f1); next_size=${next_size:-0}
    local grew=$((next_size - prev_size))
    prev_size=$next_size
    if [ "$grew" -lt 5120 ]; then
      # <5 MB this pass and nothing completed: the runner IP is likely
      # burned (Cloudflare penalty windows on Azure IPs last many minutes
      # — more passes here are wasted minutes). Exit fast so a job re-run
      # can draw a fresh IP; partial progress is preserved by the
      # rolling-key cache save in the workflow.
      zero_progress=$((zero_progress + 1))
    else
      zero_progress=0
    fi
    if [ "$zero_progress" -ge 2 ]; then
      echo "::error::runner IP appears rate-limit burned (2 passes, no progress). Re-run the failed job to draw a fresh runner — partial libs ($((prev_size / 1024)) MB) were cached and will be resumed."
      exit 2
    fi
    local backoff=$((45 + RANDOM % 30))
    echo "pass $pass: +$((grew / 1024)) MB; waiting on: ${failures[*]} — backing off ${backoff}s"
    sleep "$backoff"
  done
  echo "::error::subtrees still incomplete after $max_passes passes: ${failures[*]}"
  echo "::error::partial libs ($((prev_size / 1024)) MB) were cached; re-run to resume."
  exit 2
}

main
