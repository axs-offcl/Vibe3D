@echo off
rem ============================================================
rem  Vibe3D portable launcher.
rem
rem  Keeps preferences inside this folder (%HERE%config) so a
rem  stale userpref.blend saved by another Blender build can
rem  never crash Vibe3D at startup, and Vibe3D never touches the
rem  settings of a separately installed Blender.
rem
rem  Extra args pass through:  launch_vibe3d.bat --factory-startup
rem ============================================================
setlocal
set "HERE=%~dp0"
if not exist "%HERE%config" mkdir "%HERE%config"
if not exist "%HERE%autosave" mkdir "%HERE%autosave"
set "BLENDER_USER_CONFIG=%HERE%config"
set "BLENDER_USER_AUTOSAVE=%HERE%autosave"
start "" "%HERE%Vibe3D.exe" %*
endlocal
