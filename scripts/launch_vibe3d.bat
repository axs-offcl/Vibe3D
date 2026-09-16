@echo off
rem ============================================================
rem  Vibe3D launcher.
rem
rem  Since the portable-mode fix, double-clicking Vibe3D.exe
rem  directly is also safe: the binary detects the 2.83\config
rem  folder next to it and keeps ALL user data (prefs, autosave)
rem  inside the bundle. This launcher exists for optional
rem  arguments and a friendly entry point.
rem
rem  Extra args pass through:  launch_vibe3d.bat --factory-startup
rem ============================================================
start "" "%~dp0Vibe3D.exe" %*
