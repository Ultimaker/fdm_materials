project(fdm_materials NONE)

cmake_minimum_required(VERSION 2.8.12)

set(INSTALL_PATH "share/cura/resources/materials" CACHE PATH "The path to install the materials to. Should ideally be relative to CMAKE_INSTALL_PREFIX")

file(GLOB _files *.fdm_material)

install(FILES ${_files} DESTINATION ${INSTALL_PATH})
