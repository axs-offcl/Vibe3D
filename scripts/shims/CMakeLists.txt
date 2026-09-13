# Vibe3D — OIIO link shims for the r62438 libs under MSVC 14.5x.
#
# Two dllimport inline members are absent from the 2020-built
# OpenImageIO.dll (VS2019 always auto-inlined them; MSVC 14.5x emits real
# __imp_ calls — run #25's exactly-two LNK2019s):
#   __imp_??0string_view@OpenImageIO_v2_1@@QEAA@XZ
#   __imp_?is_array@TypeDesc@OpenImageIO_v2_1@@QEBA_NXZ
#
# scripts/oiio_link_shims.cpp carries hand-written bodies mirroring the
# header definitions (layouts verified against string_view.h / typedesc.h).
# /ALTERNATENAME is consulted by the linker ONLY when the primary symbol is
# unresolved, so this is inert against any lib that exports the real thing.
#
# Self-contained mini CMake project: the workflow configures+builds it
# FIRST (cmake -S scripts/shims -B build/shims), producing
# build/shims/Release/oiio_link_shims.lib. The main configure then links
# that .lib into Vibe3D.exe together with the /ALTERNATENAME flags via
# CMAKE_EXE_LINKER_FLAGS.

cmake_minimum_required(VERSION 3.5)
project(vibe3d_oiio_shims CXX)

add_library(oiio_link_shims STATIC oiio_link_shims.cpp)
target_compile_definitions(oiio_link_shims PRIVATE NDEBUG)
if(MSVC)
  target_compile_options(oiio_link_shims PRIVATE /O2 /MD)
endif()
