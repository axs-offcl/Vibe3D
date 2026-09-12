# Vibe3D Master Plan

## 1. Project Goal

- Strip down Blender 2.83 LTS C/C++ source to bare essentials for 3D texture
  painting and UV mapping.
- Remove: Cycles, Bullet Physics, Fluid Simulation, Sculpting, Animation modules.
- Customize UI branding: rename executable and splash screen to "Vibe3D".

## Build constraints (measured 2026-09-12)

- Disk C: ~7.3 GB free — TIGHT for Blender source + win64 libs + build tree.
  Full build trees often exceed 10 GB. Free space or use a second drive
  before fetching libs.
- Toolchain found: MSVC 14.44 (VS 2022 BuildTools) + Windows SDK 10.0.26100.0.
  `cl.exe` present. No ninja / g++ on PATH. CMake 4.3.3 present.
- Blender 2.83 era expects VS 2019 (v142) / CMake 3.x; VS 2022 + CMake 4.x
  will likely need compatibility flags (`-DCMAKE_POLICY_VERSION_MINIMUM=3.5`,
  `-T v142` if installed, else patch).

## Next steps

1. Free disk (target 30 GB+ free) or point `source/` + build dir at D:.
2. Fetch Blender 2.83 LTS source (shallow, ~1 GB):
   `bash scripts/fetch-blender.sh` (clones `v2.83.20` into `source/`)
3. Fetch Windows precompiled libs (svn, several GB) — biggest disk cost.
4. Apply branding patch, then strip modules one at a time with a build check
   after each removal.
