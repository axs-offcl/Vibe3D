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
3. ✅ **DONE** — svn fetch hardened: jittered exponential backoff
   (60·attempt + 0–29 s jitter × 5 attempts). Portable-zip approach,
   r62700 pin + libs cache kept as-is.
4. ✅ **DONE** — pre-flight diagnostics step (disk free, toolchain versions)
   and configure-failure log dump (CMakeError.log / configure log tails).
5. ⏳ **IN PROGRESS** — pushed; iterating on real CI logs. Remaining risk
   class is MSVC-2022/2026 compile errors in 2.83 code beyond C5287 — fixes
   belong in `apply-msvc-patches.py` (its designed role), not toolchain
   fights.

## Risks / caveats

- Dev sandbox is Linux (no MSVC): CI is the only real test bed.
- Runner RAM/link time: fallback is `--parallel 2` if Release linking OOMs
  or the 360-min timeout gets tight.
- Keep the single-job structure; no premature splitting.
