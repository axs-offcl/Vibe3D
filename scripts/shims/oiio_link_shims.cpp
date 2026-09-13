/*
 * Vibe3D — link shims for OIIO 2.1.15 (r62438 libs) under MSVC 14.5x.
 *
 * Two OIIO inline members are defined in-class (dllimport) but the
 * 2020-built OpenImageIO.dll never exported them:
 *   - OpenImageIO_v2_1::string_view::string_view()   (default ctor)
 *         ??0string_view@OpenImageIO_v2_1@@QEAA@XZ
 *   - OpenImageIO_v2_1::TypeDesc::is_array() const
 *         ?is_array@TypeDesc@OpenImageIO_v2_1@@QEBA_NXZ
 * VS2019's compiler auto-inlined such members at every call site, so the
 * missing exports never mattered. MSVC 14.5x emits real __imp_ calls for
 * out-of-line-emitted inline functions instead (run #25: LNK2019 x2, and
 * the import lib verifiably lacks both symbols).
 *
 * Bodies mirror the r62438 header definitions exactly:
 *   string_view()          -> init(nullptr, 0): m_chars=nullptr, m_len=0
 *   is_array()             -> arraylen != 0
 * Layouts verified against the headers: string_view = {const char*, size_t};
 * TypeDesc = {u8 basetype, u8 aggregate, u8 vecsemantics, u8 reserved,
 * int arraylen} -> arraylen at byte offset 8.
 *
 * Wired in via /alternatename (see the workflow's Configure step), which
 * the linker consults ONLY when the primary symbol is unresolved — a
 * future lib build that exports the real thing automatically wins.
 */

extern "C" __declspec(noinline) void*
vibe3d_oiio_stringview_default_ctor(void* self)
{
    void** fields = static_cast<void**>(self);
    fields[0] = nullptr; /* m_chars */
    fields[1] = nullptr; /* m_len = 0 */
    return self;
}

extern "C" __declspec(noinline) bool
vibe3d_oiio_typedesc_is_array(const void* typedesc)
{
    const unsigned char* base = static_cast<const unsigned char*>(typedesc);
    int arraylen;
    /* little-endian int at offset 8 */
    arraylen = static_cast<int>(base[8]) | (static_cast<int>(base[9]) << 8) |
               (static_cast<int>(base[10]) << 16) |
               (static_cast<int>(base[11]) << 24);
    return arraylen != 0;
}
