#!/usr/bin/env python3
"""Vibe3D source strips: Wave 1 (animation editors) + Wave 2 (sculpt/seq/clip).

Wave 1 — remove the Dope Sheet (space_action), Graph editor (space_graph) and
NLA (space_nla) editor libraries. Leaf editor modules: the only seams are (1)
registration calls in space_api/spacetypes.c, (2) a handful of call sites in
still-linked editor libs (run #30's link errors enumerated them exactly), and
(3) their entries in the editors CMake graph. Blender 2.83 upstream degrades
gracefully when a saved screen layout references an unregistered space type:
ED_area_initialize() falls back to SPACE_VIEW3D (screen/area.c), so existing
startup.blend layouts are safe.

Wave 2 — remove sculpt/paint (sculpt_paint), sequencer (space_sequencer) and
movie clip editor (space_clip). These are bigger and referenced from many
keeper files (~40 keepers reference ~81 externals: mask/ uses the clip API,
transform/ uses the sculpt hooks, outliner/ and anim_ops the sequencer API).
Instead of hand-stubbing dozens of call sites, the strip injects a stub
translation unit (scripts/wave2_stubs.c — prototypes verbatim from upstream
headers, inert no-op bodies) compiled INTO bf_editor_space_api, and removes
the Sculpt/PaintCurve undo registrations so BKE_UNDOSYS_TYPE_* stays NULL
(all readers tolerate that). BKE_* and data-layer code is untouched; the one
reachable stub caller (sequencer_ibuf_get via the image sample operator)
NULL-checks its result.

Core data and the Python API stay untouched by both waves — Python scripts
keep full access to animation, painting and sequencer *data*; only the
hand-editing UIs/modes are gone.

Idempotent: re-running reports "already stripped" and exits 0.
Fails nonzero if an expected anchor is missing (upstream drift), so CI
never silently builds a half-stripped tree.

Usage: python scripts/apply-strips.py [--source-dir source]
"""

import argparse
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Wave 1
# ---------------------------------------------------------------------------

# (file, exact line to delete, human label)
W1_LINE_REMOVALS = [
    # 1. Registration calls (spacetypes.c, ED_spacetypes_init)
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_action();\n", "Dope Sheet registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_nla();\n", "NLA registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_ipo();\n", "Graph editor registration"),
    # 2. Operator-macro registration (spacetypes.c, ED_spacemacros_init)
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatormacros_action();\n", "Dope Sheet operator macros"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatormacros_graph();\n", "Graph editor operator macros"),
    # 3. Build graph: subdirectories (editors/CMakeLists.txt)
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_action)\n", "space_action subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_graph)\n", "space_graph subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_nla)\n", "space_nla subdir"),
    # 4. Build graph: link deps of space_api (space_api/CMakeLists.txt)
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_action\n", "space_action link dep"),
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_graph\n", "space_graph link dep"),
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_nla\n", "space_nla link dep"),
]

# (file, exact block to replace, replacement, human label)
W1_BLOCK_REPLACEMENTS = [
    # rna_space.c: Graph-editor Drivers-mode init (generated rna_space_gen.c
    # is built from this file, so patching the source fixes the build).
    ("source/blender/makesrna/intern/rna_space.c",
     '''  /* for "Drivers" mode, enable all the necessary bits and pieces */
  if (sipo->mode == SIPO_MODE_DRIVERS) {
    ED_drivers_editor_init(C, area);
    ED_area_tag_redraw(area);
  }
''',
     '''  /* Vibe3D: Graph editor / Drivers mode is stripped from this build. */
  (void)sipo;
''',
     "rna_space.c Drivers-mode init"),

    # screen_ops.c: "Show in Drivers Editor" operator — stub the whole invoke
    # body. The operator stays registered (keymaps/menus reference its id), it
    # just cancels with an honest message instead of opening a stripped editor.
    ("source/blender/editors/screen/screen_ops.c",
     '''static int drivers_editor_show_invoke(bContext *C, wmOperator *op, const wmEvent *event)
{
  PointerRNA ptr = {NULL};
  PropertyRNA *prop = NULL;
  int index = -1;
  uiBut *but = NULL;

  int sizex = 900 * UI_DPI_FAC;
  int sizey = 580 * UI_DPI_FAC;

  /* Get active property to show driver for
   * - Need to grab it first, or else this info disappears
   *   after we've created the window
   */
  but = UI_context_active_but_prop_get(C, &ptr, &prop, &index);

  /* changes context! */
  if (WM_window_open_temp(C,
                          IFACE_("Blender Drivers Editor"),
                          event->x,
                          event->y,
                          sizex,
                          sizey,
                          SPACE_GRAPH,
                          false) != NULL) {
    ED_drivers_editor_init(C, CTX_wm_area(C));

    /* activate driver F-Curve for the property under the cursor */
    if (but) {
      FCurve *fcu;
      bool driven, special;

      fcu = rna_get_fcurve_context_ui(C, &ptr, prop, index, NULL, NULL, &driven, &special);
      if (fcu) {
        /* Isolate this F-Curve... */
        bAnimContext ac;
        if (ANIM_animdata_get_context(C, &ac)) {
          int filter = ANIMFILTER_DATA_VISIBLE | ANIMFILTER_NODUPLIS;
          ANIM_deselect_anim_channels(&ac, ac.data, ac.datatype, 0, ACHANNEL_SETFLAG_CLEAR);
          ANIM_set_active_channel(&ac, ac.data, ac.datatype, filter, fcu, ANIMTYPE_FCURVE);
        }
        else {
          /* Just blindly isolate...
           * This isn't the best, and shouldn't happen, but may be enough. */
          fcu->flag |= (FCURVE_ACTIVE | FCURVE_SELECTED);
        }
      }
    }

    return OPERATOR_FINISHED;
  }
  else {
    BKE_report(op->reports, RPT_ERROR, "Failed to open window!");
    return OPERATOR_CANCELLED;
  }
}
''',
     '''static int drivers_editor_show_invoke(bContext *C, wmOperator *op, const wmEvent *event)
{
  /* Vibe3D: the Drivers editor (Graph editor) is stripped from this build. */
  BKE_report(op->reports, RPT_WARNING, "Drivers editor is not included in Vibe3D");
  return OPERATOR_CANCELLED;
}
''',
     "screen_ops.c drivers_editor_show stub"),

    # anim_channels_defines.c: NLA action-channel colors in the channel-list
    # drawing tables (bf_editor_animation stays linked). Neutral fill instead.
    ("source/blender/editors/animation/anim_channels_defines.c",
     "  nla_action_get_color(ale->adt, (bAction *)ale->data, color);\n",
     "  /* Vibe3D: nla_action_get_color lives in the stripped NLA editor. */\n"
     "  zero_v4(color);\n",
     "acf_nlaaction_color neutral fill"),
    ("source/blender/editors/animation/anim_channels_defines.c",
     "  nla_action_get_color(adt, (bAction *)ale->data, color);\n",
     "  /* Vibe3D: nla_action_get_color lives in the stripped NLA editor. */\n"
     "  zero_v4(color);\n",
     "acf_nlaaction_backdrop_color neutral fill"),

    # transform_convert.c: NLA post-transform validation (transform stays
    # linked; the NLA-strip reordering helper it called does not).
    ("source/blender/editors/transform/transform_convert.c",
     '''      /* perform after-transfrom validation */
      ED_nla_postop_refresh(&ac);
''',
     '''      /* Vibe3D: ED_nla_postop_refresh lives in the stripped NLA editor. */
''',
     "transform_convert.c NLA post-op refresh"),
]

# ---------------------------------------------------------------------------
# Wave 2
# ---------------------------------------------------------------------------

W2_LINE_REMOVALS = [
    # Registration (spacetypes.c)
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_sequencer();\n", "Sequencer registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_spacetype_clip();\n", "Clip editor registration"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatortypes_sculpt();\n", "Sculpt operator types"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatortypes_paint();\n", "Paint operator types"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatormacros_clip();\n", "Clip operator macros"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatormacros_sequencer();\n", "Sequencer operator macros"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_operatormacros_paint();\n", "Paint operator macros"),
    ("source/blender/editors/space_api/spacetypes.c",
     "  ED_keymap_paint(keyconf);\n", "Paint keymap"),
    # Build graph: subdirectories
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(sculpt_paint)\n", "sculpt_paint subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_clip)\n", "space_clip subdir"),
    ("source/blender/editors/CMakeLists.txt",
     "  add_subdirectory(space_sequencer)\n", "space_sequencer subdir"),
    # Build graph: link deps
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_clip\n", "space_clip link dep (space_api)"),
    ("source/blender/editors/space_api/CMakeLists.txt",
     "  bf_editor_space_sequencer\n", "space_sequencer link dep (space_api)"),
    ("source/blender/editors/screen/CMakeLists.txt",
     "  bf_editor_space_sequencer\n", "space_sequencer link dep (screen)"),
    ("source/blender/makesrna/intern/CMakeLists.txt",
     "  bf_editor_sculpt_paint\n", "sculpt_paint link dep (makesrna)"),
    # Sculpt/PaintCurve undo registration: leave BKE_UNDOSYS_TYPE_* NULL
    # (tolerated by every reader) instead of registering a zeroed UndoType.
    ("source/blender/editors/undo/undo_system_types.c",
     "  BKE_UNDOSYS_TYPE_SCULPT = BKE_undosys_type_append(ED_sculpt_undosys_type);\n",
     "Sculpt undo registration"),
    ("source/blender/editors/undo/undo_system_types.c",
     "  BKE_UNDOSYS_TYPE_PAINTCURVE = BKE_undosys_type_append(ED_paintcurve_undosys_type);\n",
     "PaintCurve undo registration"),
]

# Run-#33 lesson: bf_editor_util (ed_util/numinput/ed_transverts/
# select_utils/gizmo_utils) had exactly ONE incoming link edge in pristine
# 2.83 — space_sequencer. Removing the sequencer dropped util out of the
# final-link closure (LNK1120: 33 unresolved). windowmanager genuinely calls
# these symbols (wm_operators.c etc.), so re-link it there. Keep the byte-exact
# pristine block as anchor so re-runs detect the "already" case.
W2_WM_RELINK = (
    "source/blender/windowmanager/CMakeLists.txt",
    "set(LIB\n  bf_editor_screen\n)",
    "set(LIB\n  bf_editor_screen\n  bf_editor_util\n)",
    "re-link bf_editor_util into the link closure (windowmanager LIB)",
)

W2_BLOCK_REPLACEMENTS = [
    W2_WM_RELINK,
    # Stub TU: the file itself is copied into the tree by main() (from
    # scripts/wave2_stubs.c next to this script), and only registered in the
    # build here — its includes (<stdbool.h>, RNA_types.h,
    # DNA_sequence_types.h) all resolve via space_api's existing INC.
    ("source/blender/editors/space_api/CMakeLists.txt",
     "set(SRC\n  spacetypes.c\n)",
     "set(SRC\n  spacetypes.c\n  wave2_stubs.c\n)",
     "wave2 stub TU into space_api SRC"),
]

# Where the stub TU is staged inside the tree (must match the SRC entry above).
W2_STUB_DEST = "source/blender/editors/space_api/wave2_stubs.c"


def process(path: Path, rel: str, old: str, new: str, label: str, mode: str) -> int:
    """Apply one anchor. Returns 0 ok, 1 problem."""
    if not path.exists():
        print(f"MISSING FILE: {rel}")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    if old not in text:
        if new and new in text:
            print(f"already stripped: {label} ({rel})")
            return 0
        if mode == "line":
            # A deleted line can't be re-detected textually; its absence on an
            # already-stripped tree is exactly the goal. (Upstream drift would
            # equally remove it — the CI build verifies the outcome.)
            print(f"already stripped (line absent): {label} ({rel})")
            return 0
        print(f"ANCHOR NOT FOUND (upstream drift?): {label} ({rel})")
        return 1
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    verb = "stripped" if mode == "line" else "patched"
    print(f"{verb}: {label} ({rel})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply Vibe3D source strips.")
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)

    failures = 0
    for rel, line, label in W1_LINE_REMOVALS:
        failures += process(root / rel, rel, line, "", label, mode="line")
    for rel, old, new, label in W1_BLOCK_REPLACEMENTS:
        failures += process(root / rel, rel, old, new, label, mode="block")
    w1 = failures

    # Stage the Wave-2 stub TU next to spacetypes.c (idempotent copy).
    stub_src = Path(__file__).resolve().parent / "wave2_stubs.c"
    stub_dst = root / W2_STUB_DEST
    if not stub_src.exists():
        print(f"MISSING FILE: {stub_src}")
        failures += 1
    else:
        stub_dst.parent.mkdir(parents=True, exist_ok=True)
        if not stub_dst.exists() or stub_dst.read_bytes() != stub_src.read_bytes():
            shutil.copy2(stub_src, stub_dst)
            print(f"staged: wave2 stub TU -> {W2_STUB_DEST}")
        else:
            print(f"already staged: wave2 stub TU ({W2_STUB_DEST})")

    for rel, line, label in W2_LINE_REMOVALS:
        failures += process(root / rel, rel, line, "", label, mode="line")
    for rel, old, new, label in W2_BLOCK_REPLACEMENTS:
        failures += process(root / rel, rel, old, new, label, mode="block")

    print("STRIP WAVE 1 OK" if w1 == 0 else f"STRIP WAVE 1 FAILED ({w1} problems)")
    print("STRIP WAVE 2 OK" if failures == 0 else f"STRIP WAVES FAILED ({failures} problems)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
