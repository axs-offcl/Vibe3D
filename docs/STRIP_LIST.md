# Vibe3D strip list (Blender 2.83 LTS)

Flags verified against upstream `v2.83.20` CMakeLists.txt (`option(WITH_...)`).
Rule: disable at CMake level first, delete source only after a green build.
Goal context: Vibe3D is a lightweight, scriptable Blender host (see
PROJECT_PLAN.md) — everything below serves binary size, build time and UI
focus, never at the cost of the Python API.

## Phase 1 — CMake flags (in CI workflow now)

| Module | CMake flag | Dir (for later deletion) | Status |
|---|---|---|---|
| Cycles renderer | `WITH_CYCLES=OFF` | `source/intern/cycles` | flagged in CI |
| Bullet Physics | `WITH_BULLET=OFF` | `source/extern/bullet*` | flagged in CI |
| Fluid (Mantaflow) | `WITH_MOD_FLUID=OFF` | `source/intern/mantaflow` | flagged in CI |
| Ocean sim | `WITH_MOD_OCEANSIM=OFF` | `source/source/blender/blenkernel/intern/ocean*` | flagged in CI |
| Compositor | `WITH_COMPOSITOR=OFF` | `source/source/blender/compositor` | flagged in CI |
| Freestyle | `WITH_FREESTYLE=OFF` | `source/source/blender/freestyle` | flagged in CI |
| OpenVDB | `WITH_OPENVDB=OFF` | `source/extern/openvdb` | flagged in CI |
| Alembic | `WITH_ALEMBIC=OFF` | `source/extern/alembic` | flagged in CI |
| USD | `WITH_USD=OFF` | `source/extern/USD` | flagged in CI |
| OpenCollada | `WITH_OPENCOLLADA=OFF` | `source/extern/opencollada` | flagged in CI |

Lightness flags (upstream-supported OFF configs, verified safe):

| Flag | What it drops | Status |
|---|---|---|
| `WITH_INPUT_NDOF=OFF` | 3D-mouse (SpaceNavigator) drivers | in CI |
| `WITH_INTERNATIONAL=OFF` | i18n translations + fallback fonts (UI stays English) | in CI |
| `WITH_OPENSUBDIV=OFF` | GPU subdivision surface evaluator (internal fallback kept) | in CI |

## Phase 2 (Waves) — source-level removals (via scripts/apply-strips.py)

Each wave is a set of line-level strips (registration calls + CMake build
graph entries) in `scripts/apply-strips.py`, applied in CI before configure.
Safe by upstream design: an unregistered space type in a saved layout falls
back to the 3D Viewport (`ED_area_initialize`, editors/screen/area.c).

### Wave 1 — animation editors (active)

| Module | Anchor removed | Where | Status |
|---|---|---|---|
| Dope Sheet (`space_action`) | `ED_spacetype_action()` + subdir + link dep | spacetypes.c, editors/CMakeLists.txt, space_api/CMakeLists.txt | in CI |
| Graph editor (`space_graph`) | `ED_spacetype_ipo()` + subdir + link dep | same three files | in CI |
| NLA (`space_nla`) | `ED_spacetype_nla()` + subdir + link dep | same three files | in CI |

Note: animation *data* (keyframes, fcurves, constraints) and the Python API
stay fully intact — only the hand-editing UIs are removed.

### Later waves (planned, verify deps before each)

| Module | Dir | Notes |
|---|---|---|
| Sculpt mode (keep paint/UV) | `source/source/blender/editors/sculpt_paint/sculpt*` | PBVH machinery is entangled with mesh eval; needs a dep pass |
| Sequencer | `source/source/blender/editors/space_sequencer` | Video editing UI; render path dep to verify |
| Clip / movie clip editor | `source/source/blender/editors/space_clip` | Motion-tracking UI; unrelated to scripting host |

## Keep (core of the scripting host)

3D Viewport, UV/Image editor, texture paint, Outliner, Properties,
Python console + text editor, import/export, full animation **data** and
**Python API** (only the editing UIs go), and — from Phase 4 — the floating
side panel that hosts user script packs.

Log every removal in `docs/removal-log.md` with build result.
