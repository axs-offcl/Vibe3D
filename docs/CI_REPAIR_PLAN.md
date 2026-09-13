# CI repair plan — `.github/workflows/build-vibe3d.yml`

Status: `windows-latest` build red (runs #10–#12: choco SVN failures →
win64_vc15 path → SVN 429 rate limits). Everything below was probed live on
2026-09-13 against upstream `v2.83.20` and `svn.blender.org`.

## Verified working (no change needed)

| Item | Result |
|---|---|
| Branding/patch script anchors (15 strings) | all present in upstream v2.83.20 |
| `WITH_*` CMake flags (10) | all exist as `option(...)` in v2.83.20 |
| `cmake_minimum_required(3.5)` | confirms the `CMAKE_POLICY_VERSION_MINIMUM=3.5` workaround |
| `svn.blender.org` | alive (Cloudflare-fronted) — 429s are shared-IP rate limits, not repo death |
| `trunk/lib/win64_vc15` pinned at r62700 | exists and contains `python/37/` (HEAD only has `311/`; `platform_win32.cmake:372` hardcodes `PYTHON_VERSION 3.7`, so the pin is safe) |
| VisualSVN `Apache-Subversion-1.14.5.zip` | 200 OK (4.2 MB); `bin/svn.exe` + DLLs at zip root — the `$env:USERPROFILE\svn\bin` PATH entry is exactly right |

## Confirmed workflow bugs

1. **Rename step self-sabotage.** `apply-branding.py` inserts
   `set_target_properties(blender PROPERTIES OUTPUT_NAME Vibe3D)`, so the
   build emits `Vibe3D.exe` directly and `blender.exe` never exists. The
   "Rename to Vibe3D.exe" step does `Get-ChildItem -Filter blender.exe` and
   throws "blender.exe not found" — killing an otherwise good 2–3 h build.
2. **`scripts/apply-msvc-patches.py` is untracked and never called.** The
   C5287 fix (MSVC 19.51 promoting enum-flag OR warnings under `/WX`) never
   reaches CI. It must be committed and wired into the workflow.

## Fix steps

1. ✅ **DONE** — "Rename to Vibe3D.exe" replaced by "Verify Vibe3D.exe":
   accepts `Vibe3D.exe` (expected) or `blender.exe` (fallback); fails only
   if neither exists. Artifact glob `build/**/Vibe3D.exe` unchanged.
2. ✅ **DONE** — `apply-msvc-patches.py` committed and wired in right after
   branding: `python scripts/apply-msvc-patches.py --source-dir source`
   (idempotent, fails loudly on upstream drift).
3. ✅ **DONE** — svn fetch v3 (`scripts/fetch-win64-libs.sh`):
   per-subtree fetch of only the ~23 dirs the stripped build references
   (skips llvm/osl/OpenImageDenoise/embree/usd/alembic/opencollada/
   openvdb/blosc/nanovdb/shaderc/vulkan/hidapi/potrace/haru/zstd —
   ~6 GB of dead weight incl. the llvm/debug 429 magnet), peg-revision
   URLs, `svn cleanup` + `svn checkout --force` resume rounds,
   sentinel-gated success, concurrency-serialized runs. See "Run history".
4. ✅ **DONE** — pre-flight diagnostics step (disk free, toolchain versions)
   and configure-failure log dump (CMakeError.log / configure log tails).
5. ⏳ **IN PROGRESS** — next unknown is the compile itself: MSVC-2022/2026
   era errors in 2.83 code beyond C5287 belong in `apply-msvc-patches.py`
   (its designed role), not toolchain fights.

## Run history & diagnosis trail

| Run | Commit | Outcome | Lesson |
|---|---|---|---|
| #12 and earlier | 8c58c4b↓ | fetch failures | choco svn, wrong paths — pre-diagnosis era |
| #13 | c316e4b | fetch failed, 5 wasted rounds | jittered backoff alone useless: instant E160013 (peg bug) + partial tree was deleted each round |
| #14 | ccf9572 | same signature | parallel runs amplified the 429 storm |
| probe #1 | ccf9572 | pinpointed cause | HTTPS 200, svn fine, `svn info` OK; checkout died in ~1 s = E160013 peg-revision bug |
| probe #2 | c906107 | **SUCCESS — 8.0 GB in 1 round (~21 min)** | peg URL fixes E160013; a solo run needs NO resume rounds |
| #15/#16 | c906107/214cb84 | fetch "completed" at 3.4 GB → configure died on `python/37/include/Python.h` | parallel runs share the 429 budget; `svn update` returned success on an incomplete tree (exit code lies) |
| #17 | 777fb9f | failed after 9 rounds (377M→1.7G) | resume mechanics work; every 429 landed in llvm/debug — we were pulling ~6 GB of dead weight through the limiter |
| #18 | 5d45511 | cancelled | docs-only push; would have burned rate budget against #19 |
| #19 | a91add4 | failed, 7 small subtrees done | selective fetch validated: smalls complete in seconds; boost hit the 429 wall and the IP stayed walled 11 min |
| #20 | cc7708e | failed fast (8m27s), banked 54 MB | rolling cache works ("Cache saved ... -34777300641-1"); burned-IP fail-fast keeps each attempt cheap |
| #21 | 8d3a7a0 | failed, 54→110 MB banked | compounding across runs proven end-to-end; fixed 6-pass cap stopped a still-flowing IP |
| #22 | 5974b30 | fetch+configure PASSED, build died at 10m40s | three era-gap classes, see "Compile-era error classes" below |
| #23 | 16c55d0 | pending | r62438 era-correct libs + audaspace <string> + /wd5287 |

## Compile-era error classes (run #22, first real compile)

| Class | Evidence | Fix |
|---|---|---|
| OCIO API era mismatch | `ocio_impl.cc`: `applyRGB`/`getGpuShaderText` not a member, float→double, `DisplayTransformRcPtr` gone | r62700 libs are 3.0-era (OCIO v2). Re-pinned to **r62438** = tree as of 2.83 release day (2020-06-09): OCIO v1 API + python/37, all 22 sentinels verified |
| Missing `<string>` | 150+ audaspace errors, root `C2039 'string': is not a member of 'std'` in `DeviceManager.h(46)` | 14.5x STL no longer drags `<string>` in via `<unordered_map>`; patch script adds `#include <string>` to the two audaspace headers |
| C5287 under /WX | `BKE_customdata.h(496)` (usage!) and `bmesh_operators.c(311)` despite definition-level cast | warning class silenced compiler-wide via `/wd5287` injected into `platform_win32.cmake` |
| pugixml | in 2.83's hardcoded paths only inside `if(WITH_CYCLES_OSL)`; absent at r62438 | removed from fetch table |

## svn.blender.org rate-limit reality (measured 2026-09-13)

- Cloudflare-fronted; cuts transfers with HTTP 429 after roughly
  100–150 MB bursts (residential IP) or near-instantly (Azure runner IPs
  shared with other tenants).
- **IP lottery model** (runs #2/#19/#20 evidence): a fresh runner IP can
  pull the full 8 GB in one ~21-minute sitting (probe #2); a burned one
  gets ~20 MB and then instant 429s for many minutes — 30–60 s backoffs
  never lifted it (#19/#20).
- `svn update` on an interrupted checkout can return success while files
  are missing. `svn checkout --force` re-run in the same wc is faithful:
  existing files kept, missing re-fetched (verified locally: 142→196 MB
  resume of python/37).

## Completion runbook (if the fetch keeps failing)

The fetch is now a lottery ticket + compounding bank (rolling cache):

1. Each attempt banks its partial tree (`win64-vc15-r62438-<run>` keys,
   saved `if: always()`), and re-attempts resume from the newest one.
2. Subtrees are ordered big-first, so even ~20 MB-budget attempts bank
   the most valuable bytes first.
3. A burned IP fails fast (~8 min) with exit 2 and a clear "re-run me"
   error — **re-run the failed job** (`Re-run failed jobs` on the run
   page, or push anything to main) until an attempt lands a fresh IP
   with real budget. Probe #2 shows one lucky IP finishes the whole
   remaining fetch in a single pass.
4. Worst case, ~10 attempts compound the ~2 GB selective set at
   ~50 MB/run — tedious but converging. The 7 small subtrees are
   already banked as of run #20.

## Risks / caveats

- Dev sandbox is Linux (no MSVC): CI is the only real test bed.
- Runner RAM/link time: fallback is `--parallel 2` if Release linking OOMs
  or the 360-min timeout gets tight.
- Keep the single-job structure; no premature splitting.
