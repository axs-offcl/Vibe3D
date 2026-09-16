# GUI smoke test: opens Vibe3D with the prototype registered, screenshots the
# window after the first redraws, writes a marker file with the outcome, then
# hard-exits (wm.quit_blender() from a timer AVs in stock 2.83.20 — verified
# on official blender.exe too — so we never touch the quit path).

import bpy
import os
import sys
import tempfile

D = os.path.join(tempfile.gettempdir(), "vibetest")
MARK = os.path.join(D, "gui_mark.txt")
SHOT = os.path.join(D, "panel.png")


def mark(stage, extra=""):
    with open(MARK, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (stage, extra))


def _snap():
    try:
        bpy.ops.screen.screenshot(filepath=SHOT)
        mark("snap", "saved=%s" % os.path.exists(SHOT))
    except Exception as e:
        mark("snap", "FAILED %r" % e)
    return None


def _bye():
    os._exit(0)


sys.path.insert(0, r"C:\Users\A-SX\Documents\Vibe3D\scripts")
mark("start", bpy.app.version_string)

import proto_panel
proto_panel.register()
mark("registered")

# center-ish placement for a 1280x720 window
proto_panel.PANEL["x"] = 220
proto_panel.PANEL["y"] = 260

bpy.app.timers.register(_snap, first_interval=2.0)
bpy.app.timers.register(_bye, first_interval=6.0)
mark("armed")
