/* Vibe3D Wave-2 stub library.
 *
 * Defines the symbols that still-linked code references after removing the
 * sculpt/paint, sequencer and clip editor modules (docs/STRIP_LIST.md,
 * Wave 2). Compiled into bf_editor_space_api next to spacetypes.c.
 *
 * Bodies are inert no-ops on code paths that can no longer be reached:
 * the operators and space types that called them are not registered, and
 * entry points that remain reachable (e.g. sequencer_ibuf_get via the image
 * sample operator) return NULL/false, which upstream callers already
 * handle. Sculpt/PaintCurve undo registration is a no-op, leaving the
 * BKE_UNDOSYS_TYPE_* globals NULL — they are only dereferenced when the
 * corresponding undo types are used, which cannot happen here.
 *
 * Prototypes were extracted verbatim from upstream v2.83.20 headers
 * (BKE_paint.h, ED_clip.h, ED_paint.h, ED_sculpt.h, ED_sequencer.h,
 * ED_object.h, ED_image.h, ED_space_api.h, UI_interface.h,
 * space_sequencer/sequencer_intern.h) and are structurally independent of
 * those headers: every parameter type is `struct`-prefixed except
 * PointerRNA (RNA_types.h) and Sequence (DNA_sequence_types.h).
 */
#include <stdbool.h>

#include "RNA_types.h"
#include "DNA_sequence_types.h"

/* transform_generics.c still calls this on the modal-transform path even
 * with sculpt mode stripped (flag-guarded at runtime, not compiled out). */
void ED_sculpt_update_modal_transform(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
}

void BKE_paint_data_warning(struct ReportList *reports, bool uvs, bool mat, bool tex, bool stencil)
{
  /* Vibe3D stub: feature stripped. */
  (void)reports;
  (void)uvs;
  (void)mat;
  (void)tex;
  (void)stencil;
}

bool BKE_paint_proj_mesh_data_check(struct Scene *scene,
                                    struct Object *ob,
                                    bool *uvs,
                                    bool *mat,
                                    bool *tex,
                                    bool *stencil)
{
  /* Vibe3D stub: feature stripped. */
  (void)scene;
  (void)ob;
  if (uvs) {
    *uvs = false;
  }
  if (mat) {
    *mat = false;
  }
  if (tex) {
    *tex = false;
  }
  if (stencil) {
    *stencil = false;
  }
  return false;
}

bool ED_clip_can_select(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

void ED_clip_mouse_pos(struct SpaceClip *sc, struct ARegion *region, const int mval[2], float co[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)region;
  (void)mval;
  (void)co;
}

void ED_clip_point_stable_pos(struct SpaceClip *sc,
                              struct ARegion *region,
                              float x,
                              float y,
                              float *xr,
                              float *yr)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)region;
  (void)x;
  (void)y;
  (void)xr;
  (void)yr;
}

void ED_clip_point_stable_pos__reverse(struct SpaceClip *sc,
                                       struct ARegion *region,
                                       const float co[2],
                                       float r_co[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)region;
  (void)co;
  (void)r_co;
}

void ED_clip_point_undistorted_pos(struct SpaceClip *sc, const float co[2], float r_co[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)co;
  (void)r_co;
}

void ED_clip_select_all(struct SpaceClip *sc, int action, bool *r_has_selection)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)action;
  if (r_has_selection) {
    *r_has_selection = false;
  }
}

void ED_clip_update_frame(const struct Main *mainp, int cfra)
{
  /* Vibe3D stub: feature stripped. */
  (void)mainp;
  (void)cfra;
}

bool ED_clip_view_selection(const struct bContext *C, struct ARegion *region, bool fit)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)region;
  (void)fit;
  return false;
}

void ED_imapaint_bucket_fill(struct bContext *C,
                             float color[3],
                             struct wmOperator *op,
                             const int mouse[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)color;
  (void)op;
  (void)mouse;
}

void ED_imapaint_clear_partial_redraw(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_imapaint_dirty_region(struct Image *ima,
                              struct ImBuf *ibuf,
                              struct ImageUser *iuser,
                              int x,
                              int y,
                              int w,
                              int h,
                              bool find_old)
{
  /* Vibe3D stub: feature stripped. */
  (void)ima;
  (void)ibuf;
  (void)iuser;
  (void)x;
  (void)y;
  (void)w;
  (void)h;
  (void)find_old;
}

void ED_keymap_paint(struct wmKeyConfig *keyconf)
{
  /* Vibe3D stub: feature stripped. */
  (void)keyconf;
}

void ED_object_sculptmode_enter(struct bContext *C,
                                struct Depsgraph *depsgraph,
                                struct ReportList *reports)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)depsgraph;
  (void)reports;
}

void ED_object_sculptmode_enter_ex(struct Main *bmain,
                                   struct Depsgraph *depsgraph,
                                   struct Scene *scene,
                                   struct Object *ob,
                                   const bool force_dyntopo,
                                   struct ReportList *reports)
{
  /* Vibe3D stub: feature stripped. */
  (void)bmain;
  (void)depsgraph;
  (void)scene;
  (void)ob;
  (void)force_dyntopo;
  (void)reports;
}

void ED_object_sculptmode_exit(struct bContext *C, struct Depsgraph *depsgraph)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)depsgraph;
}

void ED_object_sculptmode_exit_ex(struct Main *bmain,
                                  struct Depsgraph *depsgraph,
                                  struct Scene *scene,
                                  struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)bmain;
  (void)depsgraph;
  (void)scene;
  (void)ob;
}

void ED_object_vpaintmode_enter(struct bContext *C, struct Depsgraph *depsgraph)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)depsgraph;
}

void ED_object_vpaintmode_enter_ex(struct Main *bmain,
                                   struct Depsgraph *depsgraph,
                                   struct wmWindowManager *wm,
                                   struct Scene *scene,
                                   struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)bmain;
  (void)depsgraph;
  (void)wm;
  (void)scene;
  (void)ob;
}

void ED_object_vpaintmode_exit(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
}

void ED_object_vpaintmode_exit_ex(struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)ob;
}

void ED_object_wpaintmode_enter(struct bContext *C, struct Depsgraph *depsgraph)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)depsgraph;
}

void ED_object_wpaintmode_enter_ex(struct Main *bmain,
                                   struct Depsgraph *depsgraph,
                                   struct wmWindowManager *wm,
                                   struct Scene *scene,
                                   struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)bmain;
  (void)depsgraph;
  (void)wm;
  (void)scene;
  (void)ob;
}

void ED_object_wpaintmode_exit(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
}

void ED_object_wpaintmode_exit_ex(struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)ob;
}

void ED_operatormacros_clip(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_operatormacros_paint(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_operatormacros_sequencer(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_operatortypes_paint(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_operatortypes_sculpt(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_paintcurve_undo_push_begin(const char *name)
{
  /* Vibe3D stub: feature stripped. */
  (void)name;
}

void ED_paintcurve_undo_push_end(void)
{
  /* Vibe3D stub: feature stripped. */
}

void ED_paintcurve_undosys_type(struct UndoType *ut)
{
  /* Vibe3D stub: feature stripped; PaintCurve undo type stays unregistered
   * (BKE_UNDOSYS_TYPE_PAINTCURVE remains NULL, which callers tolerate). */
  (void)ut;
}

void ED_sculpt_end_transform(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
}

void ED_sculpt_init_transform(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
}

bool ED_sculpt_mask_box_select(struct bContext *C,
                               struct ViewContext *vc,
                               const struct rcti *rect,
                               bool select)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)vc;
  (void)rect;
  (void)select;
  return false;
}

void ED_sculpt_redraw_planes_get(float planes[4][4], struct ARegion *region, struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  int i, j;
  (void)region;
  (void)ob;
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      planes[i][j] = 0.0f;
    }
  }
}

void ED_sculpt_undo_geometry_begin(struct Object *ob, const char *name)
{
  /* Vibe3D stub: feature stripped. */
  (void)ob;
  (void)name;
}

void ED_sculpt_undo_geometry_end(struct Object *ob)
{
  /* Vibe3D stub: feature stripped. */
  (void)ob;
}

void ED_sculpt_undo_push_multires_mesh_begin(struct bContext *C, const char *str)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)str;
}

void ED_sculpt_undo_push_multires_mesh_end(struct bContext *C, const char *str)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)str;
}

void ED_sculpt_undosys_type(struct UndoType *ut)
{
  /* Vibe3D stub: feature stripped; Sculpt undo type stays unregistered
   * (BKE_UNDOSYS_TYPE_SCULPT remains NULL, which callers tolerate). */
  (void)ut;
}

void ED_sequencer_deselect_all(struct Scene *scene)
{
  /* Vibe3D stub: feature stripped. */
  (void)scene;
}

void ED_sequencer_select_sequence_single(struct Scene *scene,
                                         struct Sequence *seq,
                                         bool deselect_all)
{
  /* Vibe3D stub: feature stripped. */
  (void)scene;
  (void)seq;
  (void)deselect_all;
}

void ED_sequencer_special_preview_clear(void)
{
  /* Vibe3D stub: feature stripped. */
}

Sequence *ED_sequencer_special_preview_get(void)
{
  /* Vibe3D stub: feature stripped. */
  return NULL;
}

void ED_sequencer_special_preview_set(struct bContext *C, const int mval[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)mval;
}

bool ED_space_clip_check_show_maskedit(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return false;
}

bool ED_space_clip_check_show_trackedit(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return false;
}

bool ED_space_clip_color_sample(struct SpaceClip *sc,
                                struct ARegion *region,
                                int mval[2],
                                float r_col[3])
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)region;
  (void)mval;
  (void)r_col;
  return false;
}

void ED_space_clip_get_aspect(struct SpaceClip *sc, float *aspx, float *aspy)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  if (aspx) {
    *aspx = 1.0f;
  }
  if (aspy) {
    *aspy = 1.0f;
  }
}

void ED_space_clip_get_aspect_dimension_aware(struct SpaceClip *sc, float *aspx, float *aspy)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  if (aspx) {
    *aspx = 1.0f;
  }
  if (aspy) {
    *aspy = 1.0f;
  }
}

struct ImBuf *ED_space_clip_get_buffer(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return NULL;
}

struct MovieClip *ED_space_clip_get_clip(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return NULL;
}

int ED_space_clip_get_clip_frame_number(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return 0;
}

struct Mask *ED_space_clip_get_mask(struct SpaceClip *sc)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  return NULL;
}

void ED_space_clip_get_size(struct SpaceClip *sc, int *width, int *height)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  if (width) {
    *width = 0;
  }
  if (height) {
    *height = 0;
  }
}

void ED_space_clip_get_size_fl(struct SpaceClip *sc, float size[2])
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  size[0] = 0.0f;
  size[1] = 0.0f;
}

struct ImBuf *ED_space_clip_get_stable_buffer(struct SpaceClip *sc,
                                              float loc[2],
                                              float *scale,
                                              float *angle)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)loc;
  (void)scale;
  (void)angle;
  return NULL;
}

void ED_space_clip_get_zoom(struct SpaceClip *sc,
                            struct ARegion *region,
                            float *zoomx,
                            float *zoomy)
{
  /* Vibe3D stub: feature stripped. */
  (void)sc;
  (void)region;
  if (zoomx) {
    *zoomx = 1.0f;
  }
  if (zoomy) {
    *zoomy = 1.0f;
  }
}

bool ED_space_clip_maskedit_mask_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

bool ED_space_clip_maskedit_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

bool ED_space_clip_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

void ED_space_clip_set_clip(struct bContext *C,
                            struct bScreen *screen,
                            struct SpaceClip *sc,
                            struct MovieClip *clip)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)screen;
  (void)sc;
  (void)clip;
}

void ED_space_clip_set_mask(struct bContext *C, struct SpaceClip *sc, struct Mask *mask)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  (void)sc;
  (void)mask;
}

bool ED_space_clip_tracking_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

bool ED_space_clip_view_clip_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

void ED_space_image_paint_update(struct Main *bmain,
                                 struct wmWindowManager *wm,
                                 struct Scene *scene)
{
  /* Vibe3D stub: feature stripped (prototype from ED_image.h). */
  (void)bmain;
  (void)wm;
  (void)scene;
}

bool ED_space_sequencer_check_show_imbuf(struct SpaceSeq *sseq)
{
  /* Vibe3D stub: feature stripped. */
  (void)sseq;
  return false;
}

bool ED_space_sequencer_check_show_maskedit(struct SpaceSeq *sseq, struct Scene *scene)
{
  /* Vibe3D stub: feature stripped. */
  (void)sseq;
  (void)scene;
  return false;
}

bool ED_space_sequencer_check_show_strip(struct SpaceSeq *sseq)
{
  /* Vibe3D stub: feature stripped. */
  (void)sseq;
  return false;
}

bool ED_space_sequencer_maskedit_mask_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

bool ED_space_sequencer_maskedit_poll(struct bContext *C)
{
  /* Vibe3D stub: feature stripped. */
  (void)C;
  return false;
}

void ED_spacetype_clip(void)
{
  /* Vibe3D stub: feature stripped; clip space type stays unregistered
   * (saved layouts fall back to the 3D Viewport, see area.c). */
}

void ED_spacetype_sequencer(void)
{
  /* Vibe3D stub: feature stripped; sequencer space type stays unregistered
   * (saved layouts fall back to the 3D Viewport, see area.c). */
}

/* sequencer_ibuf_get: space_sequencer/sequencer_draw.c. Its one reachable
 * caller (image sample-info operator in util/ed_util_imbuf.c) NULL-checks
 * the result, so returning NULL is safe. */
struct ImBuf *sequencer_ibuf_get(struct Main *bmain,
                                 struct Depsgraph *depsgraph,
                                 struct Scene *scene,
                                 struct SpaceSeq *sseq,
                                 int cfra,
                                 int frame_ofs,
                                 const char *viewname)
{
  /* Vibe3D stub: feature stripped. */
  (void)bmain;
  (void)depsgraph;
  (void)scene;
  (void)sseq;
  (void)cfra;
  (void)frame_ofs;
  (void)viewname;
  return NULL;
}

void uiTemplateMarker(struct uiLayout *layout,
                      struct PointerRNA *ptr,
                      const char *propname,
                      PointerRNA *userptr,
                      PointerRNA *trackptr,
                      bool compact)
{
  /* Vibe3D stub: feature stripped. */
  (void)layout;
  (void)ptr;
  (void)propname;
  (void)userptr;
  (void)trackptr;
  (void)compact;
}

void uiTemplateMovieClip(struct uiLayout *layout,
                         struct bContext *C,
                         struct PointerRNA *ptr,
                         const char *propname,
                         bool compact)
{
  /* Vibe3D stub: feature stripped. */
  (void)layout;
  (void)C;
  (void)ptr;
  (void)propname;
  (void)compact;
}

void uiTemplateMovieclipInformation(struct uiLayout *layout,
                                    struct PointerRNA *ptr,
                                    const char *propname,
                                    struct PointerRNA *userptr)
{
  /* Vibe3D stub: feature stripped. */
  (void)layout;
  (void)ptr;
  (void)propname;
  (void)userptr;
}

void uiTemplateTrack(struct uiLayout *layout, struct PointerRNA *ptr, const char *propname)
{
  /* Vibe3D stub: feature stripped. */
  (void)layout;
  (void)ptr;
  (void)propname;
}
