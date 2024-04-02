# set required cmake version
cmake_minimum_required(VERSION 3.20)

project(
    xyz
    LANGUAGES CXX
    VERSION 0.1.0
    DESCRIPTION "quantum computing library"
)

option(BUILD_XYZ_BINDINGS "Build the XYZ Python bindings" ON)
option(BUILD_XYZ_TESTS "Build the XYZ tests" ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

set(XYZ_SOURCE_DIR ${CMAKE_SOURCE_DIR})

include_directories(${XYZ_SOURCE_DIR}/include)
add_subdirectory(${XYZ_SOURCE_DIR}/lib)
add_subdirectory(${XYZ_SOURCE_DIR}/tools)

if (BUILD_XYZ_BINDINGS)
    add_subdirectory(${XYZ_SOURCE_DIR}/bindings)
endif()

if (BUILD_XYZ_TESTS)
    enable_testing()
    add_subdirectory(${XYZ_SOURCE_DIR}/tests)
endif()