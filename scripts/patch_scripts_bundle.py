#!/usr/bin/env python
"""Patch the bundled 2.83 Python UI layer for the Vibe3D strip.

Two problems appear when the stock release/scripts tree runs on a binary
whose Wave 1/2 editor libs are removed:

1. `bl_ui/__init__.py` registers every module's classes in one loop; the
   first class bound to a stripped space (Dope Sheet, Graph, NLA,
   Sequencer, Clip) raises "Region not found in space type" and aborts the
   whole loop — leaving later modules (space_view3d, space_topbar, ...)
   unregistered. Symptom: `TOPBAR_MT_file_new` missing, io_* addons failing
   with AttributeError on `TOPBAR_MT_file_import`.
2. Any leftover failure then kills registration silently mid-list.

Fix: drop the stripped spaces' UI modules entirely and make per-class
registration non-fatal. Idempotent: re-running on a patched tree is a no-op.

Usage: python patch_scripts_bundle.py <path-to-scripts-dir>
"""

import re
import sys
from pathlib import Path

STRIPPED_UI_MODULES = (
    "space_clip",
    "space_dopesheet",
    "space_graph",
    "space_nla",
    "space_sequencer",
)

STRIPPED_SPACE_TYPES = (
    "'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR',\n"
    "                'SEQUENCE_EDITOR', 'CLIP_EDITOR'"
)


def patch_init(scripts: Path) -> None:
    p = scripts / "startup" / "bl_ui" / "__init__.py"
    src = p.read_text(encoding="utf-8")

    changed = False
    for mod in STRIPPED_UI_MODULES:
        pat = r'^\s*"%s",\s*\n' % re.escape(mod)
        new_src, n = re.subn(pat, "", src, flags=re.M)
        if n:
            print(f"removed bl_ui module entry: {mod} ({n})")
            src = new_src
            changed = True

    old_reg = (
        "def register():\n"
        "    from bpy.utils import register_class\n"
        "    for mod in _modules_loaded:\n"
        "        for cls in mod.classes:\n"
        "            register_class(cls)"
    )
    new_reg = (
        "def register():\n"
        "    from bpy.utils import register_class\n"
        "    # Vibe3D: skip UI classes bound to stripped editor spaces instead\n"
        "    # of aborting the whole bl_ui registration at the first failure.\n"
        "    stripped = {%s}\n"
        "    for mod in _modules_loaded:\n"
        "        for cls in mod.classes:\n"
        "            if getattr(cls, \"bl_space_type\", None) in stripped:\n"
        "                continue\n"
        "            try:\n"
        "                register_class(cls)\n"
        "            except Exception:\n"
        "                import traceback\n"
        "                traceback.print_exc()" % STRIPPED_SPACE_TYPES
    )
    if old_reg in src:
        src = src.replace(old_reg, new_reg, 1)
        print("patched bl_ui register(): skip stripped spaces, non-fatal")
        changed = True
    elif "Vibe3D: skip UI classes bound to stripped editor spaces" in src:
        print("already patched: bl_ui register()")
    else:
        print("WARNING: bl_ui register() anchor not found (upstream drift?)")

    if changed:
        p.write_text(src, encoding="utf-8", newline="\n")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    scripts = Path(sys.argv[1])
    if not (scripts / "startup" / "bl_ui" / "__init__.py").exists():
        print(f"not a scripts dir: {scripts}")
        return 2
    patch_init(scripts)
    print("SCRIPTS PATCH OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
