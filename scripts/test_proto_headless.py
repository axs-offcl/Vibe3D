# Headless validation of the panel prototype against the real Vibe3D.exe.
# Exercises everything that does not need an OpenGL context: import, class
# registration, rect math, operator entry points, handler add/remove, and a
# simulated drag + button press through the operator's invoke/modal methods.

import sys, os
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proto_panel

print(proto_panel.TAG + "import OK")
proto_panel.register()
print(proto_panel.TAG + "register OK")

p = proto_panel.PANEL
# 1. rect math sanity
left, bottom, right, top, btn, close = proto_panel._rects()
assert right - left == p["w"], "width math"
assert top - bottom == p["title_h"] + p["body_h"], "height math"
assert btn[0] > left and btn[2] < right and btn[1] > bottom and btn[3] < top, "button inside panel"
assert close[2] <= right and close[3] <= top, "close inside panel"
print(proto_panel.TAG + "rect math OK")

# 2. draw handler callable with a fake GL context absent? draw_panel touches
# gpu/bgl only inside _rect(); exercising it needs a context, so in background
# mode we only verify the non-GL part: _rects + text metrics are skipped.

# 3. drag simulation: click in title bar, then modal MOUSEMOVE events
import types


class FakeEvent:
    def __init__(self, mx, my, type=None, value=None):
        self.mouse_region_x, self.mouse_region_y = mx, my
        self.type, self.value = type, value


class FakeWindow:
    pass


class FakeWM:
    def modal_handler_add(self, op):
        print(proto_panel.TAG + "modal_handler_add called")
        return True


class FakeCtx:
    window = FakeWindow()
    window_manager = FakeWM()


ctx = FakeCtx()


class DummySelf:
    def report(self, *a):
        print(proto_panel.TAG + "report:", a)


OT = proto_panel.VIBE3D_OT_panel_click

# title-bar press at (left + 100, top - 15)
ev = FakeEvent(left + 100, top - 15, 'LEFTMOUSE', 'PRESS')
ret = OT.invoke(DummySelf(), ctx, ev)
print(proto_panel.TAG + "invoke(title) ->", ret)
assert ret == {'RUNNING_MODAL'}, "title press should start modal drag"
assert p["drag"] is not None, "drag state armed"

ev = FakeEvent(left + 160, top + 40, 'MOUSEMOVE')
ret = OT.modal(DummySelf(), ctx, ev)
print(proto_panel.TAG + "modal(move) ->", ret)
assert ret == {'RUNNING_MODAL'}
assert p["x"] > left, "panel moved right"
assert p["y"] > bottom, "panel moved up"

ev = FakeEvent(left + 160, top + 40, 'LEFTMOUSE', 'RELEASE')
ret = OT.modal(DummySelf(), ctx, ev)
print(proto_panel.TAG + "modal(release) ->", ret)
assert ret == {'FINISHED'}
assert p["drag"] is None, "drag cleared"

# 4. button press: cube should be created
# rects moved with the drag -- recompute from the new panel position
left, bottom, right, top, btn, close = proto_panel._rects()
names_before = set(bpy.data.objects.keys())
ev = FakeEvent((btn[0] + btn[2]) // 2, (btn[1] + btn[3]) // 2, 'LEFTMOUSE', 'PRESS')
ret = OT.invoke(DummySelf(), ctx, ev)
print(proto_panel.TAG + "invoke(button) ->", ret)
assert ret == {'FINISHED'}
new_names = set(bpy.data.objects.keys()) - names_before
assert len(new_names) == 1, "Add Cube created exactly one object: %r" % new_names
assert all(bpy.data.objects[n].type == 'MESH' for n in new_names), "created object is a mesh"

# 5. click outside: must PASS_THROUGH (viewport stays usable)
ev = FakeEvent(left - 50, bottom - 50, 'LEFTMOUSE', 'PRESS')
ret = OT.invoke(DummySelf(), ctx, ev)
assert ret == {'PASS_THROUGH'}, "outside click passes through"

# 6. close button hides; toggle re-shows
ev = FakeEvent((close[0] + close[2]) // 2, (close[1] + close[3]) // 2, 'LEFTMOUSE', 'PRESS')
ret = OT.invoke(DummySelf(), ctx, ev)
assert ret == {'FINISHED'} and p["open"] is False, "close hides panel"
bpy.ops.vibe3d.panel_toggle()
assert p["open"] is True, "toggle re-shows"

# 7. idempotent teardown
proto_panel.unregister()
proto_panel.unregister()  # second call must not raise
print(proto_panel.TAG + "unregister OK (idempotent)")

print(proto_panel.TAG + "ALL HEADLESS CHECKS PASSED")
