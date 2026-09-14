# Vibe3D — A Lightweight, Highly Scriptable Blender Fork

Vibe3D is a fork of Blender 2.83 LTS (C/C++) with one goal: be the fastest,
simplest 3D base a script author could ask for. It sits in the gap between
3ds Max and Blender — Blender's toolset and Python API, minus the heavy
machinery most workflows never touch.

It is **not** trying to be a full 3D suite. It is a lean scripting host:

- **Fast** — aggressive module stripping (Cycles, physics, sculpting,
  animation editors, sequencer…) keeps compile time, binary size and
  startup snappy.
- **Scriptable first** — the primary UI is a floating side panel where you
  add, run and manage lightweight Python scripts (in the spirit of KAM
  scripts in 3ds Max).
- **Shareable** — scripts are plain `.py` files; drop a folder in, share a
  pack, build your own personal toolset.

> **Why it exists:** GTA San Andreas / MTA SA skinning (DFF/TXD) is the
> author's personal use case and the reason the project started — it is the
> first script pack target, not the project's identity. Vibe3D is for any
> personal workflow that wants a small, fast, script-driven Blender.

## Quick start (Codespaces / Linux)

```bash
bash scripts/fetch-blender.sh   # shallow-clones Blender v2.83.20 into source/
```

`source/` and `lib/` are git-ignored (fetched, never committed).
See `PROJECT_PLAN.md` for the roadmap and `docs/STRIP_LIST.md` for the
module removal list with verified CMake flags.

## CI build (Windows)

`.github/workflows/build-vibe3d.yml` on `windows-latest` compiles the
stripped source into `Vibe3D.exe` and uploads it as the
`Vibe3D-windows-x64` artifact. Status: **green** (runs #27–#29).

## Workspace layout

- `source/` — upstream Blender 2.83 LTS source (fetched, patched in CI)
- `.github/workflows/` — CI build for Windows
- `docs/` — plans, strip list, build/repair notes
- `scripts/` — fetch, branding, MSVC-compat, strip and dashboard scripts
- `vibe/` — Vibe3D art (splash, icons) and future script-pack scaffolding

## Status

- [x] Workspace created, env checked
- [x] Setup script + CI workflow added
- [x] Blender 2.83 LTS source fetched
- [x] Branding patch (exe name `Vibe3D.exe` + splash/icon hooks)
- [x] First Windows build **green** (`Vibe3D.exe`, artifact uploaded)
- [x] CMake-level module strip (Cycles, Bullet, Fluid, Compositor, …)
- [ ] Phase 3 — source-level strip (animation editors, sculpt, …)
- [ ] Phase 4 — scripting platform UI (floating side panel, script manager)
- [ ] Phase 5 — script packs (KAM-style ports; GTA SA pack as first example)
