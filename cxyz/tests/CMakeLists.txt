find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

add_executable(runUnitTests qgates.cpp)
target_link_libraries(runUnitTests ${GTEST_LIBRARIES} pthread)
target_link_libraries(runUnitTests cxyz)

add_test(NAME cxyz-test COMMAND runUnitTests)