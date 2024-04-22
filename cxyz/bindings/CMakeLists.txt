find_package(Python 3.10 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)
if (pybind11_FOUND)
    message(STATUS "Found pybind11 v${pybind11_VERSION}: ${pybind11_INCLUDE_DIRS}")
    pybind11_add_module(xyz MODULE xyz.cpp)
endif()

# Link the Python interpreter
target_link_libraries(xyz PRIVATE cxyz)

