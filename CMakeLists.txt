project(fdm_materials NONE)

cmake_minimum_required(VERSION 2.8.12)

include(CMakePackageConfigHelpers)

option(EMBEDDED "Build for Ultimaker Embedded software" OFF)

if(NOT EMBEDDED)
    set(INSTALL_PATH "share/cura/resources/materials"
        CACHE PATH
        "The path to install the materials to. Should ideally be relative to CMAKE_INSTALL_PREFIX"
        )
else()
    # Then we're cmaking for Jedi
    set(INSTALL_PATH "share/fdm_materials"
        CACHE STRING
        "Destination to install the materials to. Should be relative to CMAKE_INSTALL_PREFIX")
    
    if(IS_ABSOLUTE ${INSTALL_PATH})
        set(INSTALL_PATH ${INSTALL_PATH})
    else()
        set(INSTALL_PATH ${CMAKE_INSTALL_PREFIX}/${INSTALL_PATH})
    endif()
endif()

file(GLOB _files *.fdm_material *.sig)

# Determine version number
find_package(Git)

set(GIT_VERSION "Unknown")
if(GIT_FOUND)
    execute_process(
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND ${GIT_EXECUTABLE} describe --tags --exact-match --dirty
        OUTPUT_VARIABLE GIT_VERSION
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(GIT_VERSION)
        set(CPACK_PACKAGE_VERSION "${GIT_VERSION}")
    else()
        execute_process(
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            COMMAND ${GIT_EXECUTABLE} describe --tags --dirty
            OUTPUT_VARIABLE GIT_VERSION
            OUTPUT_STRIP_TRAILING_WHITESPACE)
    endif()
    message("Package version derived from git: ${GIT_VERSION}")
    set(CPACK_PACKAGE_VERSION "${GIT_VERSION}")
endif()

if (DEFINED ENV{CI})
    set(CPACK_PACKAGE_VERSION "${GIT_VERSION}+$ENV{CI_COMMIT_SHORT_SHA}.$ENV{CI_PIPELINE_ID}")
endif()
#

install(FILES ${_files} DESTINATION ${INSTALL_PATH})

include(CPackConfig.cmake)
