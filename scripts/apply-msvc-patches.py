#!/usr/bin/env python3
"""Vibe3D MSVC-era-gap patches — fixes Blender 2.83 source for MSVC 19.51+
(VS2022/VS2026) which windows-latest runners ship.

Usage:
    python scripts/apply-msvc-patches.py [--source-dir source]

Idempotent: safe to re-run. Exits nonzero if an anchor is missing.

Fixes:
  BKE_customdata.h — CD_FAKE enum-flag ORs trip C5287
    ("operands are different enum types") which MSVC 19.51 promotes to an
    error (/WX) in several targets. Casting the 1<<8 base to CustomDataType
    makes both OR operands the same enum type.
"""

import argparse
import sys
from pathlib import Path


def patch_bke_customdata(root: Path) -> str:
    p = root / "source" / "blender" / "blenkernel" / "BKE_customdata.h"
    if not p.exists():
        return f"MISSING FILE: {p}"
    text = p.read_text(encoding="utf-8", errors="replace")
    if "(CustomDataType)(1 << 8)" in text:
        return "already patched: BKE_customdata.h CD_FAKE cast (C5287)"
    old = "  CD_FAKE = 1 << 8,"
    new = "  CD_FAKE = (CustomDataType)(1 << 8),"
    if old not in text:
        return f"ANCHOR NOT FOUND in {p}: {old!r}"
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")
    return "patched: BKE_customdata.h CD_FAKE cast (C5287)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply MSVC-era-gap patches to Blender source.")
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)

    results = [patch_bke_customdata(root)]
    for r in results:
        print(r)
    fail = [r for r in results if r.startswith(("MISSING", "ANCHOR"))]
    print("MSVC PATCHES OK" if not fail else f"MSVC PATCHES FAILED ({len(fail)} problems)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())