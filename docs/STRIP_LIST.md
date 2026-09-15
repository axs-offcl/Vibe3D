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

### Wave 1 — animation editors (green: run #31 built + uploaded Vibe3D.exe)

| Module | Anchor removed | Where | Status |
|---|---|---|---|
| Dope Sheet (`space_action`) | `ED_spacetype_action()` + macros + subdir + link dep | spacetypes.c, editors/CMakeLists.txt, space_api/CMakeLists.txt | in CI |
| Graph editor (`space_graph`) | `ED_spacetype_ipo()` + macros + subdir + link dep | same three files | in CI |
| NLA (`space_nla`) | `ED_spacetype_nla()` + subdir + link dep | same three files | in CI |

**Out-of-lib call sites** (surfaced by run #30's link errors, fixed same wave):

| Symbol (defined in stripped lib) | Call site | Fix |
|---|---|---|
| `ED_drivers_editor_init` | `rna_space.c` (Graph Drivers-mode update) | branch replaced with comment + `(void)sipo;` |
| `ED_drivers_editor_init` | `screen_ops.c` `SCREEN_OT_drivers_editor_show` | invoke body stubbed; operator stays registered, cancels with an honest warning (keymaps/menus still reference its id) |
| `ED_operatormacros_action` / `_graph` | `spacetypes.c` `ED_spacemacros_init` | calls removed |
| `nla_action_get_color` | `anim_channels_defines.c` (2 drawing callbacks) | neutral `zero_v4(color)` fill |
| `ED_nla_postop_refresh` | `transform_convert.c` NLA branch | call removed (strip re-sorting helper; data stays consistent) |

Note: animation *data* (keyframes, fcurves, constraints) and the Python API
stay fully intact — only the hand-editing UIs are removed.

### Wave 2 — sculpt/paint, sequencer, clip editor (in CI, pending green build)

Larger modules referenced from ~40 keeper files (~81 external symbols), so
these strips use a different mechanism: instead of editing call sites, the
strip injects a stub translation unit (`scripts/wave2_stubs.c`, prototypes
verbatim from upstream headers, inert no-op bodies) compiled INTO
`bf_editor_space_api` — every keeper file keeps linking unchanged.

| Module | Anchors removed | Status |
|---|---|---|
| Sculpt + paint modes (`sculpt_paint`) | subdir, link deps (space_api + makesrna), operator-type/macro registrations, `ED_keymap_paint`, Sculpt+PaintCurve undo registrations | in CI |
| Sequencer (`space_sequencer`) | subdir, link deps (space_api + screen), registration + macros | in CI |
| Clip editor (`space_clip`) | subdir, link dep (space_api), registration + macros | in CI |

Stub semantics worth knowing:
- Sculpt/PaintCurve undo types are deliberately left **unregistered**
  (`BKE_UNDOSYS_TYPE_*` stay NULL) rather than registered as zeroed structs;
  every reader tolerates NULL and painting/sculpt undo is meaningless with
  the modes gone.
- `sequencer_ibuf_get` (image sample-info operator path) returns NULL; its
  one reachable caller already NULL-checks.
- Mode-toggle entry points (`ED_object_sculptmode_enter*` etc.) are no-ops:
  the UI buttons that called them are not registered.

### Later waves (planned, verify deps before each)

| Module | Dir | Notes |
|---|---|---|
| Grease Pencil (annotate) | `source/source/blender/editors/gpencil` | entangled with view3d annotation drawing; dep pass needed |
| Info editor (`space_info`) | `source/source/blender/editors/space_info` | log window; low value once the script host UI lands |
| Vertex/weight paint *data* stays | — | Python API untouched (mesh vertex colors remain accessible) |

## Keep (core of the scripting host)

3D Viewport, UV/Image editor, texture paint, Outliner, Properties,
Python console + text editor, import/export, full animation **data** and
**Python API** (only the editing UIs go), and — from Phase 4 — the floating
side panel that hosts user script packs.

Log every removal in `docs/removal-log.md` with build result.
