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
#36+ embeds the Vibe3D layout; run ≤ #35 embeds upstream's factory startup,
whose Timeline area is a stripped space and crashes GUI startup.)

## Easy path — the portable bundle (run #36+)

From the green run's summary page, download the
**`Vibe3D-windows-x64-portable`** artifact. It is a zip that already contains
`Vibe3D.exe + 2.83\ + blender.crt\ + all DLLs`. Then:

1. Download + unzip anywhere (e.g. `C:\Vibe3D\`).
2. Double-click **`Vibe3D.exe`** directly (or `launch_vibe3d.bat` — same
   effect, just a friendly wrapper that also accepts CLI args).
   Nothing else is needed: the private CRT (`blender.crt\`) ships the exact
   VS-Redist DLLs the CI toolset built the exe against (plus `vcomp140.dll`
   — the exe imports it), and the factory startup is baked into the exe
   itself in the Vibe3D layout.

   **Portable mode (runs #39+):** the bundle ships an empty `2.83\config\`
   folder, which Blender 2.83's built-in portable-install detection picks
   up — all user data (prefs, autosave) then lives *inside the bundle* and
   `%APPDATA%` is never read or written. Stale prefs from other Blender
   installs can't touch Vibe3D, and moving/deleting the folder = full reset.
   Your settings live in `2.83\config\userpref.blend` next to the exe.
3. Smoke test: 3D viewport orbits, add a cube (Shift+A), open the Python
   console and run `import bpy; print(bpy.app.version)`.

### If the GUI crashes on first run (atio6axx.dll / any AV at startup)

**First, check the version.** Run ≤ #38 bundles are NOT portable: launching
`Vibe3D.exe` directly reads `%APPDATA%` prefs. Run #39+ bundles are (the
`2.83\config\` folder triggers portable mode automatically). For a ≤ #38
bundle, either create the folder yourself — `mkdir 2.83\config` inside the
bundle — or fix the environment directly:

One confirmed field report: Vibe3D crashed on the user's first launch with
`EXCEPTION_ACCESS_VIOLATION ... atio6axx.dll` (the AMD OpenGL driver) after
prefs loaded fine. The binary itself is fine — on the same machine with a
fresh config it boots every time (12+ consecutive clean GUI boots observed).
The trigger was a `userpref.blend` saved earlier by another Blender build:
on load, Vibe3D re-creates GPU driver settings/GPU states from prefs that
don't match its toolset, and the AMD ICD dereferences them. The crash is
also intermittent (a race in driver state creation), so a bundle can boot
cleanly several times and still be reading poison prefs.

Fix: with a #39+ bundle this cannot happen (portable mode). Otherwise delete
the stale prefs once:
`%APPDATA%\Blender Foundation\Blender\2.83\config\userpref.blend`
(the whole `config\` folder is safe to delete — it regenerates).

Related cosmetic warnings that do NOT block startup: `wm.keymap ... unknown
operator 'CLIP_OT_*'/'SEQUENCER_OT_*'` (keymaps of deliberately stripped
spaces), the matching `property '...' not found in keymap item` spam, and —
in bundles from runs ≤ #37 — `Missing icons: ops.*.dat` (gizmo icons were
not packaged; fixed from run #38 on, alongside the launcher).

> **Run ≤ #35 caveat:** those bundles have two defects — `blender.crt\`
> misses its DLLs (loader error `0xC0000135`; fix: copy
> `msvcp140/vcruntime140/vcruntime140_1/concrt140.dll` from `C:\Windows\System32`
> — but **not** from official Blender 2.83's `blender.crt`, whose 2020-era
> DLLs crash a VS-2022 build inside MSVCP140) and upstream's embedded
> factory startup triggers a 2 MB stack overflow at GUI init
> (`0xC00000FD`; workaround: copy a clean startup into
> `%APPDATA%\Blender Foundation\Blender\2.83\config\`). Both are fixed
> from run #36 on (16 MB stack link flag + VS-Redist CRT sourcing).

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
- User preferences/cache live in the bundle's `2.83\config\` and
  `2.83\autosave\` (portable mode). Delete them to reset to factory
  defaults — `%APPDATA%` is never touched.
- If the exe starts but the UI is broken/text missing, the `2.83\datafiles\`
  copy is incomplete — recopy `fonts` and `colormanagement`.
- Phase 4 note: once the script host lands, packs go into
  `2.83\scripts\vibe3d_packs\<YourPack>\scripts\*.py` — see
  `docs/SCRIPT_HOST_DESIGN.md`.
