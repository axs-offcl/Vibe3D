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
3. ✅ **DONE** — svn fetch, final design (after 3 diagnoses):
   peg-revision URL (`win64_vc15@62700`), `svn cleanup` +
   `svn checkout --force` resume rounds, success gated on sentinel files
   on disk, runs serialized via a concurrency group. See "Run history".
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
| #17 | 777fb9f | pending | concurrency serialization + sentinel-gated `checkout --force` resume |

## svn.blender.org rate-limit reality (measured 2026-09-13)

- Cloudflare-fronted; cuts transfers with HTTP 429 after roughly
  100–150 MB bursts (residential IP) or near-instantly (Azure runner IPs
  shared with other tenants).
- A single patient client CAN pull the full 8 GB tree: probe #2 did it in
  one ~21-minute round. Keep rounds solo, keep them resumable.
- `svn update` on an interrupted checkout can return success while files
  are missing. `svn checkout --force` re-run in the same wc is faithful:
  existing files kept, missing re-fetched (verified locally: 142→196 MB
  resume of python/37).

## Risks / caveats

- Dev sandbox is Linux (no MSVC): CI is the only real test bed.
- Runner RAM/link time: fallback is `--parallel 2` if Release linking OOMs
  or the 360-min timeout gets tight.
- Keep the single-job structure; no premature splitting.
