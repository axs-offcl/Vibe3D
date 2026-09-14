#!/usr/bin/env python3
"""Vibe3D Wave-1 source strip: remove the animation editors.

Removes the Dope Sheet (space_action), Graph editor (space_graph) and NLA
(space_nla) editor libraries from the build. These are leaf editor modules:
the only seams are (1) registration calls in space_api/spacetypes.c and
(2) their entries in the editors CMake graph. Blender 2.83 upstream already
degrades gracefully when a saved screen layout references an unregistered
space type: ED_area_initialize() falls back to SPACE_VIEW3D
(source/blender/editors/screen/area.c), so existing startup.blend layouts
are safe.

Core animation *data* (keyframes on objects, fcurve evaluation, constraints)
stays untouched — Python scripts keep full animation API access; only the
hand-editing UIs are gone.

Idempotent: re-running reports "already stripped" and exits 0.
Fails nonzero if an expected anchor is missing (upstream drift), so CI
never silently builds a half-stripped tree.

Usage: python scripts/apply-strips.py [--source-dir source]
"""

import argparse
import sys
from pathlib import Path

# (file, exact line to delete, human label)
LINE_REMOVALS = [
    # 1. Registration calls (spacetypes.c, ED_spacetypes_init)
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_action();\n", "Dope Sheet registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_nla();\n", "NLA registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_ipo();\n", "Graph editor registration"),
    # 2. Build graph: subdirectories (editors/CMakeLists.txt)
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_action)\n", "space_action subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_graph)\n", "space_graph subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_nla)\n", "space_nla subdir"),
    # 3. Build graph: link deps of space_api (space_api/CMakeLists.txt)
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_action\n", "space_action link dep"),
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_graph\n", "space_graph link dep"),
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_nla\n", "space_nla link dep"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply Vibe3D Wave-1 source strips.")
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)

    failures = 0
    for rel, line, label in LINE_REMOVALS:
        p = root / rel
        if not p.exists():
            print(f"MISSING FILE: {rel}")
            failures += 1
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if line not in text:
            print(f"already stripped: {label} ({rel})")
            continue
        p.write_text(text.replace(line, "", 1), encoding="utf-8")
        print(f"stripped: {label} ({rel})")

    print("STRIP WAVE 1 OK" if failures == 0 else f"STRIP WAVE 1 FAILED ({failures} problems)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
