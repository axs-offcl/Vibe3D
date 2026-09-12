# Vibe3D strip list (Blender 2.83 LTS)

Flags verified against upstream `v2.83.20` CMakeLists.txt (`option(WITH_...)`).
Rule: disable at CMake level first, delete source only after a green build.

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

## Phase 2 — source-level removals (after first green build)

| Module | Dir | Status |
|---|---|---|
| Sculpting (keep paint/UV) | `source/source/blender/editors/sculpt_paint/sculpt*` | planned — verify deps |
| Animation editors | `source/source/blender/editors/animation` | planned — verify deps |

## Keep

Image/UV editor, texture paint, DFF/TXD pipeline deps, import/export.

Log every removal in `docs/removal-log.md` with build result.
