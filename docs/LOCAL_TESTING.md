# Testing Vibe3D.exe locally on Windows

## What the exe actually needs

`Vibe3D.exe` is a Blender 2.83 binary. A bare exe cannot start — it needs a
`2.83\` data folder beside it, plus its dependency DLLs:

| Path | Contents | Purpose |
|---|---|---|
| `2.83\scripts\` | `startup\`, `modules\`, `addons\`, `presets\` | the entire Python UI layer + `bpy` module glue |
| `2.83\datafiles\` | `colormanagement\`, `fonts\` | OCIO config + UI font |
| `2.83\python\bin`, `2.83\python\lib` | python37.dll + stdlib | embedded Python |
| `<exe dir>\*.dll` | OpenImageIO, OpenColorIO, Boost, FFmpeg, SDL, OpenAL, … | build dependencies |

(`startup.blend` is compiled into the exe as `datatoc` data in 2.83 — run
#35+ embeds the Vibe3D layout; older builds relied on `%APPDATA%`.)

## Easy path — the portable bundle (run #35+)

From the green run's summary page, download the
**`Vibe3D-windows-x64-portable`** artifact. It is a zip that already contains
`Vibe3D.exe + 2.83\ + blender.crt\ + all DLLs`. Then:

1. Download + unzip anywhere (e.g. `C:\Vibe3D\`).
2. Double-click `Vibe3D.exe`. Nothing else is needed: the private CRT
   (`blender.crt\`) and every runtime DLL ship inside, and the bundle carries
   its own `2.83\config\startup.blend` so even `%APPDATA%` is optional.
3. Smoke test: 3D viewport orbits, add a cube (Shift+A), open the Python
   console and run `import bpy; print(bpy.app.version)`.

### Prototype panel

`scripts/proto_panel.py` (in the repo) is the Phase-4 floating-panel
prototype. To try it:

```bat
cd C:\Vibe3D
Vibe3D.exe --python path\to\proto_panel.py
```

A draggable panel appears over the viewport: drag its title bar to move it,
press **Add Cube** to run a script function, press **x** to close,
`Vibe3D: Toggle Panel` (F3 search) re-shows it. All viewport navigation
keeps working underneath the panel.

## Manual path — from the `Vibe3D-windows-x64` artifact (runs ≤ #34)

Those artifacts contain the bare exe only, so you must assemble the
environment yourself:

1. Unzip the artifact to `C:\Vibe3D\`.
2. Clone the data files from the Blender 2.83 repo (or copy from any 2.83
   install you have):

   ```bat
   git clone --depth 1 --branch v2.83.20 https://github.com/blender/blender.git %TEMP%\bl283
   robocopy %TEMP%\bl283\release\scripts  C:\Vibe3D\2.83\scripts /E
   robocopy %TEMP%\bl283\release\datafiles\colormanagement C:\Vibe3D\2.83\datafiles\colormanagement /E
   robocopy %TEMP%\bl283\release\datafiles\fonts C:\Vibe3D\2.83\datafiles\fonts /E
   ```

3. Python: copy `lib\win64_vc15\python\37\{bin,lib}` from Blender's
   precompiled libs (SVN `https://svn.blender.org/svnroot/bf-blender/branches/blender-2.83-release/lib/win64_vc15/python/37/`)
   into `C:\Vibe3D\2.83\python\`, then copy `python37.dll` (and any other
   missing DLLs — the error dialog names them one at a time) next to the exe.
4. Launch from a terminal so errors are visible:

   ```bat
   cd C:\Vibe3D
   Vibe3D.exe --debug
   ```

   `--debug` prints every search path the binary tries — anything reported
   missing is exactly what to add.

## Notes

- Blender 2.83 embeds its Python: no system Python install is required or used.
- User preferences/cache land in `%APPDATA%\Vibe3D\2.83\config\` (safe to
  delete to reset).
- If the exe starts but the UI is broken/text missing, the `2.83\datafiles\`
  copy is incomplete — recopy `fonts` and `colormanagement`.
- Phase 4 note: once the script host lands, packs go into
  `2.83\scripts\vibe3d_packs\<YourPack>\scripts\*.py` — see
  `docs/SCRIPT_HOST_DESIGN.md`.
