# Vibe3D Script Host — Phase 4 design

Vibe3D is a lightweight, highly scriptable Blender fork. Its defining feature
is the **script host**: a simple panel where users drop script packs (think
KAM scripts in 3ds Max) and get buttons — one folder in, UI out.

## 1. Implementation choice: Python-driven UI, C-free for now

The user-visible question: native C/C++ panel, or Python UI hooking the C
core? Decision: **Python-driven UI shipped as a bundled add-on**
(`scripts/addons_vibe3d/vibe3d_host/`), for these reasons:

1. **Packs are dynamic data.** A folder scan must turn into buttons at
   runtime. Blender 2.83's C UI API (uiLayout, OperatorType enums, RNA
   properties) is built for *static, compiled* menus; doing dynamic
   per-file buttons in C means an OperatorProperty enum trick and a rebuild
   cycle for every host tweak. Python's `layout.operator()` + dynamic
   `EnumProperty` does this natively.
2. **Iteration speed.** The host lives in the `2.83/scripts` bundle —
   editable *by our own users* without recompiling Vibe3D.exe. A C host
   would freeze the UI behind CI builds.
3. **The C core stays untouched** → every CI fix in `apply-msvc-patches.py`
   keeps applying to pristine upstream code.
4. **It is still "native feel".** The panel is drawn by Blender's own UI
   engine (same buttons, tooltips, search as everything else) — the only
   Python is the draw callback and the dispatcher operator.

## 1a. Floating overlay panel — prototyped and validated (2026-09-16)

The user requirement sharpened: **no separate OS window** — the panel must be
an overlay *inside* the 3D Viewport (drag anywhere, stays while you work,
like KAM rollouts). Approach #1 (GPU overlay) was prototyped against the
real stripped binary (`scripts/proto_panel.py`) and validated:

- `SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_PIXEL')` draws rects
  (`gpu` + `bgl` blend) and text (`blf`) in region-local pixel space. Works.
- Interaction = a **short-lived modal operator**: a click inside the panel
  arms drag or runs the button; clicks outside `PASS_THROUGH`, so viewport
  navigation keeps working underneath. Drag-move verified end-to-end.
- Verified rendered output via `bgl.glReadPixels` of a title-bar pixel
  inside the draw handler: (0.157, 0.169, 0.220) vs draw color
  (0.16, 0.17, 0.22).
- 2.83 API notes: batch constructor is `batch_for_shader(shader, ...)`
  (format comes from the shader); `bpy.app.timers` is the sanctioned async
  path; a windowless timer has **no operator context** —
  `screen.screenshot` poll fails there.
- Known upstream quirk (not Vibe3D): timer-driven `wm.quit_blender()`
  access-violates in stock 2.83.20 (verified on official `blender.exe`).
  Test scripts must `os._exit()` instead.
- GUI-startup fix shipped with the prototype: the embedded factory
  `startup.blend` contained a Timeline area (SPACE_ACTION) whose init
  crashes in the stripped binary; `apply-strips.py` now overlays a Vibe3D
  startup (all screens scrubbed) before the blob is compiled in.

The host UI (pack scan → buttons) will render inside this same overlay
framework: each pack = a collapsible section, each script = a button row.
The v1 N-panel sidebar remains the fallback layout, sharing the same
scanner/dispatcher code.

The "floating panel" from the plan maps to two deliverables:

- **v1 (this phase):** the host UI as a **3D Viewport sidebar tab**
  (`N-panel`, category "Vibe3D") plus a default scripting workspace
  layout where it is pre-pinned. Fast, robust, ships with the bundle.
- **v2 (Phase 5, optional):** a **dedicated floating window** — one
  `wmWindow` opened via the same `WM_window_open_temp` pattern the drivers
  editor used (see `screen_ops.c`, run-#31 stub), containing a single
  editor whose draw handler shows only the host UI. The pack scanner and
  dispatcher from v1 are reused 1:1; only the window chrome is new. 2.83
  cannot dock floating windows, so v1's sidebar remains the primary UX and
  v2 is a secondary "toolbox window" toggle.

## 2. Pack format (Phase 5 contract, defined now)

```
<packs-root>/
  MyPack/
    pack.json            # {"name":"MyPack","version":"1.0","author":"...","description":"..."}
    icon.png             # optional 24x24, shown in the section header
    scripts/
      script_one.py      # one file = one button (see contract below)
      subfolder/
        nested.py        # subfolders become collapsible sub-sections
```

Scripts root resolution (first hit wins):
1. `$VIBE3D_PACKS` env var,
2. `<binary-dir>/2.83/scripts/vibe3d_packs/` (portable/installs),
3. `%APPDATA%/Vibe3D/packs/` (user-writable fallback).

**Button contract** — each `.py` exports:

```python
def vibe3d_meta():
    return {"label": "Skin Assist", "icon": "ARMATURE_DATA",
            "description": "One-click rigger helper"}

def execute(context):          # context: bpy.context
    ...                        # return {'FINISHED'} / raise = error toast
```

Fallbacks if `vibe3d_meta` is missing: filename as label, `ICON_CONSOLE`.
`register()`/`unregister()` are NOT called for pack scripts (no state, no
keymaps from packs in v1) — a pack is *data*, which is what makes packs
shareable and safely reloadable.

## 3. Runtime flow

1. **Scan** — host add-on walks the packs root; result cached, invalidated
   by directory mtime + a manual "Rescan" button. Import cost: zero until a
   button is clicked (metadata parsed with `ast`, never executed).
2. **Draw** — panel: per pack a collapsible section (`pack.icon`, name,
   version) → buttons grouped by subfolder → footer row: Rescan / Open
   packs folder / New script template.
3. **Run** — one shared operator `vibe3d.run_script(filepath=…)`:
   `importlib` load with a mtime-bumped unique module name → call
   `execute(context)` → `{'FINISHED'}`; exceptions become a red report +
   full traceback to the system console. No dialog suppression: packs get
   the same operator UX as built-ins.
4. **Manage** — per-button context menu: Edit (opens in the Vibe3D text
   editor), Reload, Reveal in Explorer, Copy path. Per-pack: Disable
   (local `disabled.json` marker), Remove.

## 4. Safety & failure modes

- `ast`-based metadata parsing means a syntax-broken script still lists and
  fails only on click, with a clean error — the panel never breaks.
- Packs run with full Python access (same trust level as any Blender
  add-on) — documented, not sandboxed, consistent with the "personal
  workflow scripts" positioning.
- A pack whose `pack.json` is invalid is skipped with a warning line in the
  panel, never fatal.

## 5. Deliberately out of scope (v1)

Docking (2.83 engine limitation), marketplace/discovery, sandboxing,
auto-update of packs, non-Windows paths beyond the 3 defaults above.
