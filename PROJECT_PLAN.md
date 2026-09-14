# Vibe3D Master Plan

## 1. Project Goal

Vibe3D is a **lightweight, highly scriptable fork of Blender 2.83 LTS** —
a fast, simple platform that bridges 3ds Max and Blender, without the heavy
machinery. Its identity:

1. **Lean core** — strip Blender down to what personal workflows actually
   use: 3D Viewport, UV/Image editor, texture paint, Outliner, Properties,
   Python console/text editor, import/export.
2. **Scriptable first** — a floating side panel serves as the primary UI:
   add, run and manage lightweight Python scripts (KAM-scripts-style).
   Scripts are shareable `.py` packs; the app is their host.
3. **Bridge, not clone** — familiar-feeling, minimal UI for artists coming
   from 3ds Max, with the full Blender Python API underneath.

> GTA SA / MTA SA skinning (DFF/TXD) is the author's personal use case and
> the original motivation. It is the first script-pack target — not the
> project's identity. Vibe3D serves any personal 3D workflow.

## Phases

- **Phase 1 — CI green** *(done: runs #27–#29)* — reproducible Windows
  build of the branded fork; see `docs/CI_REPAIR_PLAN.md`.
- **Phase 2 — CMake-level strip** *(done)* — 10+ `WITH_*` flags off
  (Cycles, Bullet, Fluid, Compositor, Freestyle, OpenVDB, Alembic, USD,
  OpenCollada, OpenSubdiv…); see `docs/STRIP_LIST.md`.
- **Phase 3 — Source-level strip** *(active)* — remove editor/UI modules
  the scripting host never needs: animation editors (Dope Sheet, Graph,
  NLA), sculpt mode, sequencer, clip/video editor, etc. Wave-by-wave,
  each gated on a green build.
- **Phase 4 — Scripting platform UI** — floating side panel (KAM-scripts
  style): script list, one-click run, per-script enable/disable, import a
  pack folder. Generic host behavior; domain logic lives in scripts.
- **Phase 5 — Script packs & ecosystem** — pack format + docs + examples.
  First pack: GTA SA (DFF/TXD skinning), ported from the author's KAM
  scripts. Anyone can build/share their own pack.

## Build constraints (measured 2026-09-12)

- Disk C: ~7.3 GB free — TIGHT for Blender source + win64 libs + build tree.
  Full build trees often exceed 10 GB. Free space or use a second drive
  before fetching libs.
- Toolchain found: MSVC 14.44 (VS 2022 BuildTools) + Windows SDK 10.0.26100.0.
  `cl.exe` present. No ninja / g++ on PATH. CMake 4.3.3 present.
- Blender 2.83 era expects VS 2019 (v142) / CMake 3.x; VS 2022 + CMake 4.x
  needs compatibility flags (`-DCMAKE_POLICY_VERSION_MINIMUM=3.5`) and the
  era-gap patches in `scripts/apply-msvc-patches.py` (see CI workflow).

## Next steps

1. Phase 3 Wave 1: strip animation editors (space_action/nla/graph) via
   `scripts/apply-strips.py` + CMake lightness flags; green CI = pass.
2. Phase 3 Wave 2+: sculpt mode, sequencer/clip editors (verify deps first).
3. Phase 4: side-panel prototype (space_script-based) in `vibe/` + CI build.
4. Phase 5: script-pack loader + GTA SA pack as the first example.
