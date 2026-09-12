# Vibe3D — Lightweight 3D Texture & Skin Editor for GTA SA / MTA SA

Forked from Blender 2.83 LTS (C/C++). Goal: strip to bare essentials for
3D texture painting + UV mapping. Target: GTA San Andreas / MTA SA skinning.

## Quick start (Codespaces / Linux)

```bash
bash scripts/fetch-blender.sh   # shallow-clones Blender v2.83.20 into source/
```

`source/` and `lib/` are git-ignored (fetched, never committed).
See `PROJECT_PLAN.md` for the master plan and `docs/STRIP_LIST.md` for the
module removal list with verified CMake flags.

## CI build (Windows)

`.github/workflows/build-vibe3d.yml` on `windows-latest` compiles the
stripped source into `Vibe3D.exe` (renamed from `blender.exe`) and uploads
it as the `Vibe3D-windows-x64` artifact.

## Workspace layout

- `source/` — upstream Blender 2.83 LTS source (fetched, untouched)
- `.github/workflows/` — CI build for Windows
- `docs/` — plans, module removal log, build notes
- `scripts/` — fetch, environment check, build scripts

## Status

- [x] Workspace created, env checked
- [x] Setup script + CI workflow added
- [ ] Blender 2.83 LTS source fetched
- [ ] Branding patch (exe name + splash)
- [ ] Modules stripped (Cycles, Bullet, Fluid, Sculpt, Animation)
- [ ] First Windows build
