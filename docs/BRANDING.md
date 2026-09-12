# Vibe3D branding map (Blender v2.83.20 upstream)

Applied by `scripts/apply-branding.py` (idempotent). All locations verified
against upstream tag `v2.83.20`.

## Window title (`source/blender/windowmanager/`)

| File:line | Code | Becomes |
|---|---|---|
| `intern/wm_window.c:490` | `"Blender%s [%s%s]"` in `wm_window_title()` | `"Vibe3D%s [%s%s]"` |
| `intern/wm_window.c:497` | `GHOST_SetTitle(win->ghostwin, "Blender")` | `"Vibe3D"` |
| `intern/wm_window.c:710` | `wm_window_ghostwindow_add(wm, "Blender", ...)` | `"Vibe3D"` |
| `intern/wm_platform_support.c:141,170` | `"Blender - "` GPU dialog titles | `"Vibe3D - "` |

## Native defaults (`intern/ghost/`)

| File:line | Code | Becomes |
|---|---|---|
| `intern/GHOST_SystemWin32.cpp:1932` | `config.pszWindowTitle = L"Blender"` | `L"Vibe3D"` |
| `intern/GHOST_SystemX11.h:46-47` | `GHOST_X11_RES_NAME/CLASS "Blender"` | `"Vibe3D"` (Linux packaging) |

## CLI banners (`source/creator/`)

| File | Code | Becomes |
|---|---|---|
| `creator_args.c` (5×) | `printf("Blender %s…` (`--version`, `--help`, engine list…) | `printf("Vibe3D %s…` |
| `creator_intern.h:58` | `BLEND_VERSION_FMT "Blender %d.%02d.%d"` | `"Vibe3D %d.%02d.%d"` |

## Executable name (`source/creator/CMakeLists.txt`)

Target stays `blender` (all deps wiring untouched); the script inserts
`set_target_properties(blender PROPERTIES OUTPUT_NAME Vibe3D)` after
`add_executable(blender …)` so the emitted file is `Vibe3D.exe`.
macOS bundle override (`OUTPUT_NAME Blender`, ~line 876) is out of scope
for the Windows-first build.

## Splash screen

`release/datafiles/splash.png` — replace with Vibe3D art via
`--splash vibe/splash.png`. The version label in `wm_splash_screen.c`
reads `BKE_blender_version_string()` (`v2.83.20`); leave as-is until we
decide Vibe3D versioning.

## Deliberately NOT touched (Phase 2+)

- `release/windows/icons/winblender.rc` — icon resource; needs Vibe3D `.ico`
  + CMake reference update.
- `wm_event_system.c` "Blender File View", `wm_playanim.c` player titles —
  cosmetic, zero user impact for a texture editor.
- Startup `.blend` branding, translations under `release/datafiles/locale`.
