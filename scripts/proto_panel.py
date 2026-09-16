# Vibe3D Phase-4 prototype: GPU-drawn floating panel inside the 3D Viewport.
#
# Demonstrates (Blender 2.83, no C changes):
#   1. A floating panel drawn over the viewport via a POST_PIXEL draw handler
#      (gpu module for geometry, blf for text) -- not a separate OS window.
#   2. Drag-to-move by its title bar through a short-lived modal operator.
#      Clicks outside the panel are PASS_THROUGH-ed, so navigation and all
#      viewport interaction keep working underneath the panel.
#   3. A working button that runs a Python function (adds a cube).
#   4. Close (X) hides the panel; "Vibe3D: Toggle Panel" (F3 search) re-shows.
#
# Run:  Vibe3D.exe <file.blend> --python scripts/proto_panel.py

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

# --------------------------------------------------------------------------
# State (shared by draw handler + modal operator)
# --------------------------------------------------------------------------

PANEL = {
    "w": 240,
    "title_h": 30,
    "body_h": 92,
    "x": 70,            # region-local, origin = bottom-left of the 3D region
    "y": 320,           # y of the panel BOTTOM
    "open": True,
    "drag": None,       # (grab_dx, grab_dy) while dragging
    "button": None,     # rect (x0, y0, x1, y1) of the Add Cube button
    "close": None,      # rect of the X button
}

COLORS = {
    "bg":    (0.09, 0.09, 0.11, 0.92),
    "title": (0.16, 0.17, 0.22, 0.96),
    "accent": (0.13, 0.45, 0.85, 1.00),
    "close": (0.55, 0.20, 0.20, 1.00),
    "border": (0.30, 0.32, 0.40, 1.00),
    "text":  (0.92, 0.93, 0.95, 1.00),
}

FONT_ID = 0
TAG = "vibe3d_proto: "


def _rect(x0, y0, x1, y1, color):
    """Two triangles covering the rect. y0 may be > y1; ordering is fixed up."""
    lo_x, hi_x = min(x0, x1), max(x0, x1)
    lo_y, hi_y = min(y0, y1), max(y0, y1)
    verts = (
        (lo_x, lo_y), (hi_x, lo_y), (hi_x, hi_y),
        (lo_x, lo_y), (hi_x, hi_y), (lo_x, hi_y),
    )
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, "TRIS", {"pos": verts})
    bgl.glEnable(bgl.GL_BLEND)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    bgl.glDisable(bgl.GL_BLEND)


def _text(x, y, size, text, color):
    blf.size(FONT_ID, size, 72)
    blf.color(FONT_ID, *color)
    blf.position(FONT_ID, x, y, 0)
    blf.draw(FONT_ID, text)


# --------------------------------------------------------------------------
# Draw handler (runs on every viewport redraw, region-local pixel space)
# --------------------------------------------------------------------------

def _rects():
    p = PANEL
    left, bottom = p["x"], p["y"]
    right = left + p["w"]
    top = bottom + p["title_h"] + p["body_h"]
    btn_h = 36
    btn = (left + 14, bottom + 14, right - 14, bottom + 14 + btn_h)
    close = (right - 26, top - 26, right - 6, top - 6)
    return left, bottom, right, top, btn, close


def _self_verify(left, right, top):
    """First-frames proof: read back one title-bar pixel through the real GL
    pipeline. A color close to COLORS["title"] means the panel is actually
    rendered (used by automated GUI checks; harmless in normal use)."""
    n = PANEL.get("_probe_frames", 0) + 1
    PANEL["_probe_frames"] = n
    if n != 3:
        return
    try:
        buf = bgl.Buffer(bgl.GL_FLOAT, 4)
        bgl.glReadPixels(left + PANEL["w"] // 2, top - 8, 1, 1,
                         bgl.GL_RGBA, bgl.GL_FLOAT, buf)
        PANEL["probe"] = tuple(round(c, 3) for c in buf)
        import os
        d = os.path.join(os.environ.get("TEMP", "/tmp"), "vibetest")
        if os.path.isdir(d):
            with open(os.path.join(d, "gui_mark.txt"), "a") as f:
                f.write("drew3 probe=%r\n" % (PANEL["probe"],))
    except Exception:
        pass  # no GL context (headless) or fs unavailable — never break drawing


def draw_panel():
    if not PANEL["open"]:
        return
    left, bottom, right, top, btn, close = _rects()
    PANEL["button"], PANEL["close"] = btn, close

    # drop-in border first (1px offset rects make a cheap border)
    _rect(left - 1, bottom - 1, right + 1, top + 1, COLORS["border"])
    _rect(left, bottom, right, top, COLORS["bg"])
    _rect(left, top - PANEL["title_h"], right, top, COLORS["title"])

    # title bar + close cross
    _text(left + 12, top - 21, 13, "Vibe3D", COLORS["text"])
    _text(right - 20, top - 21, 12, "x", (1.0, 1.0, 1.0, 0.9))

    # the one working button
    _rect(*btn, COLORS["accent"])
    blf.size(FONT_ID, 13, 72)
    tw = blf.dimensions(FONT_ID, "Add Cube")[0]
    _text((left + right - tw) / 2.0, btn[1] + 13, 13, "Add Cube", (1, 1, 1, 1))

    _self_verify(left, right, top)


# --------------------------------------------------------------------------
# Interaction: short-lived modal operator (click / drag)
# --------------------------------------------------------------------------

def _in(x, y, r):
    return r is not None and r[0] <= x <= r[2] and r[1] <= y <= r[3]


class VIBE3D_OT_panel_click(bpy.types.Operator):
    """Interact with the floating Vibe3D panel (drag title bar, press buttons)"""
    bl_idname = "vibe3d.panel_click"
    bl_label = "Vibe3D Panel Interaction"

    def invoke(self, context, event):
        if not PANEL["open"]:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        left, bottom, right, top, btn, close = _rects()
        inside = left <= mx <= right and bottom <= my <= top
        if not inside:
            return {'PASS_THROUGH'}

        if _in(mx, my, close):
            PANEL["open"] = False
            return {'FINISHED'}
        if _in(mx, my, btn):
            self.report({'INFO'}, "Vibe3D: Add Cube")
            print(TAG + "BUTTON_CLICK AddCube")
            bpy.ops.mesh.primitive_cube_add(size=2.0)
            return {'FINISHED'}
        if my >= top - PANEL["title_h"]:
            PANEL["drag"] = (mx - left, my - bottom)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {'FINISHED'}  # body click: swallowed, nothing else happens

    def modal(self, context, event):
        drag = PANEL["drag"]
        if drag is None:
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            PANEL["drag"] = None
            return {'FINISHED'}
        if event.type == 'MOUSEMOVE':
            mx, my = event.mouse_region_x, event.mouse_region_y
            PANEL["x"] = mx - drag[0]
            PANEL["y"] = my - drag[1]
        return {'RUNNING_MODAL'}


class VIBE3D_OT_panel_toggle(bpy.types.Operator):
    """Show / hide the floating Vibe3D panel"""
    bl_idname = "vibe3d.panel_toggle"
    bl_label = "Vibe3D: Toggle Panel"

    def execute(self, context):
        PANEL["open"] = not PANEL["open"]
        print(TAG + ("SHOW" if PANEL["open"] else "HIDE"))
        return {'FINISHED'}


classes = (VIBE3D_OT_panel_click, VIBE3D_OT_panel_toggle)
_handler = None


def register():
    global _handler
    for cls in classes:
        bpy.utils.register_class(cls)
    _handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_panel, (), 'WINDOW', 'POST_PIXEL')
    # Panel starts open so a bare `--python proto_panel.py` shows it.
    PANEL["open"] = True
    print(TAG + "REGISTERED")


def unregister():
    global _handler
    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, 'WINDOW')
        _handler = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass  # already unregistered -- make teardown idempotent


if __name__ == "__main__":
    register()
