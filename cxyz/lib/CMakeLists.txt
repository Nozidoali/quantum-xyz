set (LIBRARY_SOURCE_FILES
    prepare_state.cpp
    qstate.cpp
    qcircuit.cpp
)

add_library(cxyz SHARED ${LIBRARY_SOURCE_FILES})
add_subdirectory(qgate)

target_include_directories(cxyz PUBLIC ${XYZ_SOURCE_DIR}/include)