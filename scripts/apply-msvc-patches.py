#!/usr/bin/env python3
"""Vibe3D MSVC-era-gap patches — fixes Blender 2.83 source for the modern
MSVC toolset (14.5x, Visual Studio 18) that windows-latest runners ship.

Usage:
    python scripts/apply-msvc-patches.py [--source-dir source]

Idempotent: safe to re-run. Exits nonzero if an anchor is missing.

Fixes:
  1. audaspace — DeviceManager.h / IDeviceFactory.h use std::string while
     including only <memory>/<vector>/<unordered_map>. Older STL headers
     dragged <string> in transitively; the 14.5x STL does not, so every
     audaspace TU died with C2039 "'string': is not a member of 'std'"
     (run #22: 150+ errors, all cascading from these two headers).
  2. platform_win32.cmake — append /wd5287 to CMAKE_C/CXX_FLAGS. 2.83 mixes
     enum types in flag ORs all over the codebase (CD_FAKE | CD_*, BM_VERT
     slot subtypes); modern MSVC warns C5287 and 2.83 builds with /WX, so
     every instance is an error. Source-level casts cannot cover usage sites
     (run #22 errored in bmesh_operators.c even with the CD_FAKE definition
     cast), so the warning class is silenced compiler-wide.
  3. lib-side: OIIO's vendored fmt/format.h guards checked iterators with
     `#ifdef _SECURE_SCL` — true if the macro is defined AT ALL, and the
     14.5x STL defines it to 0 as a compat shim. The dead branch references
     stdext::checked_array_iterator, which modern STL removed (run #23a2:
     C2653 + ~15 cascade errors in every OIIO TU). Rewritten to a
     value-aware #if so the branch stays dead.
"""

import argparse
import sys
from pathlib import Path

# (file relative to source root, anchor, replacement, description)
TEXT_PATCHES = [
    (
        "extern/audaspace/include/devices/DeviceManager.h",
        "#include <memory>\n#include <vector>\n#include <unordered_map>",
        "#include <memory>\n#include <string>\n#include <vector>\n#include <unordered_map>",
        "audaspace DeviceManager.h: add <string> (C2039 under MSVC 14.5x STL)",
    ),
    (
        "extern/audaspace/include/devices/IDeviceFactory.h",
        '#include "respec/Specification.h"\n\n#include <memory>',
        '#include "respec/Specification.h"\n\n#include <memory>\n#include <string>',
        "audaspace IDeviceFactory.h: add <string> (C2039 under MSVC 14.5x STL)",
    ),
    (
        "build_files/cmake/platform/platform_win32.cmake",
        'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /permissive-")',
        'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /permissive-")\n'
        "  # Vibe3D: silence C5287 (mixed-enum flag ORs); /WX promotes it to an\n"
        "  # error and 2.83 mixes enum types in dozens of places.\n"
        '  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /wd5287")\n'
        '  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /wd5287")',
        "platform_win32.cmake: /wd5287 (C5287 under /WX)",
    ),
]

# Lib-side patch (outside source/): OIIO's vendored fmt header. Lives in
# lib/win64_vc15, restored fresh from cache on every run, so the patch is
# re-applied after cache restore, before configure.
LIB_FMT_REL = Path("lib") / "win64_vc15" / "OpenImageIO" / "include" / "OpenImageIO" / "fmt" / "format.h"
FMT_SECURE_SCL_OLD = "#ifdef _SECURE_SCL"
FMT_SECURE_SCL_NEW = "#if defined(_SECURE_SCL) && _SECURE_SCL"


def patch_lib_fmt(root: Path) -> str:
    """fmt (2010-era) gates checked iterators on #ifdef _SECURE_SCL; the
    14.5x STL defines it to 0 as a compat shim, making the #ifdef TRUE and
    activating a stdext::checked_array_iterator branch that no longer
    exists. Value-aware #if keeps the branch dead."""
    p = root / LIB_FMT_REL
    if not p.exists():
        return f"MISSING FILE: {p}"
    text = p.read_text(encoding="utf-8", errors="replace")
    if FMT_SECURE_SCL_NEW in text:
        return "already patched: OIIO fmt _SECURE_SCL value-aware guard"
    if FMT_SECURE_SCL_OLD not in text:
        return f"ANCHOR NOT FOUND in {p}: {FMT_SECURE_SCL_OLD!r}"
    text = text.replace(FMT_SECURE_SCL_OLD, FMT_SECURE_SCL_NEW, 1)
    p.write_text(text, encoding="utf-8", newline="")
    return "patched: OIIO fmt _SECURE_SCL value-aware guard"


def apply_text_patches(root: Path):
    results = []
    for rel, anchor, replacement, desc in TEXT_PATCHES:
        p = root / rel
        if not p.exists():
            results.append(f"MISSING FILE: {p}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        # Idempotency: detect the patch by its distinctive inserted marker.
        marker = replacement.splitlines()[-1].strip()
        if replacement in text or (marker in text and marker not in anchor):
            results.append(f"already patched: {desc}")
            continue
        if anchor not in text:
            results.append(f"ANCHOR NOT FOUND in {p}")
            continue
        text = text.replace(anchor, replacement, 1)
        p.write_text(text, encoding="utf-8", newline="")
        results.append(f"patched: {desc}")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply MSVC-era-gap patches to Blender source.")
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)

    results = apply_text_patches(root)
    results.append(patch_lib_fmt(Path(".")))  # lib/ sits next to source/ at repo root
    for r in results:
        print(r)
    fail = [r for r in results if r.startswith(("MISSING", "ANCHOR"))]
    print("MSVC PATCHES OK" if not fail else f"MSVC PATCHES FAILED ({len(fail)} problems)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
