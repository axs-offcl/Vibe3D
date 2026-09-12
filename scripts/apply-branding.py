#!/usr/bin/env python3
"""Vibe3D branding patch — renames "Blender" to "Vibe3D" in a Blender 2.83 tree.

Usage:
    python scripts/apply-branding.py [--source-dir source]
        [--splash vibe/splash.png] [--icons-dir vibe/icons]

Idempotent: safe to re-run. Exits nonzero if an expected anchor is missing
(upstream drift) or if a "Blender" title string survives in a touched file.
Splash + icons install automatically when the default vibe/ art exists.

What it changes (see docs/BRANDING.md for the full map):
  1. Window titles  -> "Vibe3D" (+ filename when a .blend is open)
  2. Win32 default window title + X11 res_name/res_class
  3. CLI --version / --help strings ("Vibe3D x.y.z")
  4. Executable output name -> Vibe3D.exe (via OUTPUT_NAME, target untouched)
  5. Splash image (only with --splash; otherwise prints a reminder)
"""

import argparse
import shutil
import sys
from pathlib import Path

APP = "Vibe3D"

# (relative path, old anchor, new text, replace_all_in_file)
TEXT_EDITS = [
    # Main window title: "Blender[*] [file.blend]" -> "Vibe3D[*] [file.blend]"
    ("source/blender/windowmanager/intern/wm_window.c",
     '"Blender%s [%s%s]"', '"Vibe3D%s [%s%s]"', False),
    # Fallback title for a fresh window.
    ("source/blender/windowmanager/intern/wm_window.c",
     'GHOST_SetTitle(win->ghostwin, "Blender")',
     'GHOST_SetTitle(win->ghostwin, "Vibe3D")', False),
    # Initial title passed when the GHOST window is created.
    ("source/blender/windowmanager/intern/wm_window.c",
     'wm_window_ghostwindow_add(wm, "Blender", win, is_dialog)',
     'wm_window_ghostwindow_add(wm, "Vibe3D", win, is_dialog)', False),
    # Win32 native default (shows before first GHOST_SetTitle).
    ("intern/ghost/intern/GHOST_SystemWin32.cpp",
     'config.pszWindowTitle = L"Blender"',
     'config.pszWindowTitle = L"Vibe3D"', False),
    # X11 window class/name (Linux; harmless on Windows, keeps packages sane).
    ("intern/ghost/intern/GHOST_SystemX11.h",
     '#  define GHOST_X11_RES_NAME "Blender"',
     '#  define GHOST_X11_RES_NAME "Vibe3D"', False),
    ("intern/ghost/intern/GHOST_SystemX11.h",
     '#  define GHOST_X11_RES_CLASS "Blender"',
     '#  define GHOST_X11_RES_CLASS "Vibe3D"', False),
    # CLI banners: printf("Blender %s\n", ...) etc.
    ("source/creator/creator_args.c",
     'printf("Blender ', 'printf("Vibe3D ', True),
    ("source/creator/creator_intern.h",
     '#  define BLEND_VERSION_FMT "Blender %d.%02d.%d"',
     '#  define BLEND_VERSION_FMT "Vibe3D %d.%02d.%d"', False),
    # GPU-support dialogs: "Blender - Limited Platform Support".
    ("source/blender/windowmanager/intern/wm_platform_support.c",
     'STR_CONCAT(title, slen, "Blender - ");',
     'STR_CONCAT(title, slen, "Vibe3D - ");', True),
    # Hidden Win32 helper windows (GLEW/XR offscreen contexts, never visible).
    ("intern/ghost/intern/GHOST_SystemWin32.cpp",
     '"BlenderGLEW"', '"Vibe3DGLEW"', False),
    ("intern/ghost/intern/GHOST_SystemWin32.cpp",
     '"Blender XR"', '"Vibe3D XR"', False),
]

# Anchor after which the exe rename is inserted (keep target name `blender`,
# just change the file it emits so all dependency wiring keeps working).
EXE_ANCHOR = "add_executable(blender ${EXETYPE} ${SRC})"
EXE_INSERT = (
    "\n# --- Vibe3D branding: emit Vibe3D.exe instead of blender.exe ---\n"
    "set_target_properties(blender PROPERTIES OUTPUT_NAME Vibe3D)\n"
)
EXE_FILE = "source/creator/CMakeLists.txt"
SPLASH_DST = "release/datafiles/splash.png"
ICON_DSTS = {
    "winblender.ico": "release/windows/icons/winblender.ico",
    "winblenderfile.ico": "release/windows/icons/winblenderfile.ico",
}


def edit_text(root: Path, rel: str, old: str, new: str, replace_all: bool) -> str:
    p = root / rel
    if not p.exists():
        return f"MISSING FILE: {rel}"
    text = p.read_text(encoding="utf-8", errors="replace")
    if new in text and old not in text:
        return f"already branded: {rel}"
    if old not in text:
        return f"ANCHOR NOT FOUND in {rel}: {old!r}"
    text = text.replace(old, new) if replace_all else text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")
    return f"patched: {rel}"


def rename_exe(root: Path) -> str:
    p = root / EXE_FILE
    text = p.read_text(encoding="utf-8", errors="replace")
    if "OUTPUT_NAME Vibe3D" in text:
        return f"already branded: {EXE_FILE}"
    if EXE_ANCHOR not in text:
        return f"ANCHOR NOT FOUND in {EXE_FILE}: {EXE_ANCHOR!r}"
    p.write_text(text.replace(EXE_ANCHOR, EXE_ANCHOR + EXE_INSERT, 1), encoding="utf-8")
    return f"patched: {EXE_FILE} (OUTPUT_NAME Vibe3D)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply Vibe3D branding to Blender source.")
    ap.add_argument("--source-dir", default="source")
    ap.add_argument("--splash", default="vibe/splash.png",
                    help="PNG to install as splash screen ('none' to skip)")
    ap.add_argument("--icons-dir", default="vibe/icons",
                    help="dir of .ico files to install ('none' to skip)")
    args = ap.parse_args()
    root = Path(args.source_dir)

    failures = 0
    for rel, old, new, all_ in TEXT_EDITS:
        msg = edit_text(root, rel, old, new, all_)
        print(msg)
        if msg.startswith(("MISSING", "ANCHOR")):
            failures += 1
    print(rename_exe(root))

    if args.splash and args.splash != "none":
        src = Path(args.splash)
        if src.exists():
            dst = root / SPLASH_DST
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"splash installed: {SPLASH_DST}")
        else:
            print(f"note: splash art missing at {src}, upstream splash kept")
    else:
        print("note: splash skipped")

    if args.icons_dir and args.icons_dir != "none":
        icons = Path(args.icons_dir)
        for name, rel in ICON_DSTS.items():
            src = icons / name
            if src.exists():
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                print(f"icon installed: {rel}")
            else:
                print(f"note: icon missing at {src}, upstream icon kept")
    else:
        print("note: icons skipped")

    # Sweep: no "Blender" title string may survive in the touched files.
    touched = {rel for rel, _, _, _ in TEXT_EDITS}
    leftovers = []
    for rel in sorted(touched):
        for i, line in enumerate((root / rel).read_text(errors="replace").splitlines(), 1):
            if '"Blender' in line or "'Blender" in line or ">Blender<" in line:
                leftovers.append(f"{rel}:{i}: {line.strip()}")
    if leftovers:
        print("LEFTOVER 'Blender' strings:")
        print("\n".join(leftovers))
        failures += 1
    print("BRANDING OK" if failures == 0 else f"BRANDING FAILED ({failures} problems)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
