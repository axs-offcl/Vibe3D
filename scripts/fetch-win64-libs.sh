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
  "boost boost include/boost/version.hpp"
  "openexr openexr include/OpenEXR/ImfVersion.h"
  "opencolorio OpenColorIO include/OpenColorIO/OpenColorABI.h"
  "OpenImageIO OpenImageIO include/OpenImageIO/version.h"
  "openjpeg openjpeg include/openjpeg-2.3/openjpeg.h"
  "pugixml pugixml include/pugixml.hpp"
  "fftw3 fftw3 include/fftw3.h"
  "sndfile sndfile include/sndfile.h"
  "openal openal include/AL/al.h"
  "sdl sdl include/SDL.h"
  "tbb tbb include/tbb/tbb.h"
  "python python/37 include/Python.h"
  "ffmpeg ffmpeg include/libavcodec/avcodec.h"
  "opensubdiv opensubdiv include/opensubdiv/version.h"
  "xr_openxr_sdk xr_openxr_sdk include/openxr/openxr.h"
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
  local failures=() item pass max_passes=12
  for pass in $(seq 1 $max_passes); do
    echo "=== pass $pass/$max_passes ==="
    failures=()
    for item in "${SUBTREES[@]}"; do
      set -- $item
      fetch_subtree "$1" "$2" "$3" || failures+=("$1")
    done
    if [ ${#failures[@]} -eq 0 ]; then
      echo "ALL SUBTREES COMPLETE ($(du -sh "$DEST" | cut -f1))"
      exit 0
    fi
    local backoff=$((20 + RANDOM % 40))
    echo "pass $pass: waiting on: ${failures[*]} — backing off ${backoff}s"
    sleep "$backoff"
  done
  echo "::error::subtrees still incomplete after $max_passes passes: ${failures[*]}"
  exit 1
}

main
