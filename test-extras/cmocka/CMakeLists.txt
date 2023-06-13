find_package(CMocka CONFIG REQUIRED)

add_executable(test_dstr test_dstr.c)
target_include_directories(test_dstr PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_dstr PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_dstr ${CMAKE_CURRENT_BINARY_DIR}/test_dstr)
