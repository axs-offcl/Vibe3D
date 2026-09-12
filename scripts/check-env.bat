@echo off
REM Vibe3D environment check — run from cmd.exe
echo === Vibe3D env check ===
git --version
cmake --version | head -n 1
where cl 2>nul || echo [missing on PATH] cl.exe — use VsDevCmd or Developer Prompt
echo MSVC:
dir "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC" 2>nul
echo Windows SDK:
dir "C:\Program Files (x86)\Windows Kits\10\Include" 2>nul
echo Disk free:
wmic logicaldisk get caption,freespace,size | findstr C:
