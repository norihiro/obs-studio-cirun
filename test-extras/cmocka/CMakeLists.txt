find_package(CMocka CONFIG REQUIRED)

add_executable(test_dstr test_dstr.c)
target_include_directories(test_dstr PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_dstr PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_dstr ${CMAKE_CURRENT_BINARY_DIR}/test_dstr)

add_executable(test_darray test_darray.c)
target_include_directories(test_darray PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_darray PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_darray ${CMAKE_CURRENT_BINARY_DIR}/test_darray)

add_executable(test_circlebuf test_circlebuf.c)
target_include_directories(test_circlebuf PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_circlebuf PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_circlebuf ${CMAKE_CURRENT_BINARY_DIR}/test_circlebuf)

add_executable(test_utf8 test_utf8.c)
target_compile_definitions(test_utf8 PUBLIC CMAKE_CURRENT_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_include_directories(test_utf8 PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_utf8 PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_utf8 ${CMAKE_CURRENT_BINARY_DIR}/test_utf8)

add_executable(test_crc32 test_crc32.c)
target_include_directories(test_crc32 PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_crc32 PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_crc32 ${CMAKE_CURRENT_BINARY_DIR}/test_crc32)

add_executable(test_fourcc test_fourcc.c)
target_include_directories(test_fourcc PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_fourcc PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_fourcc ${CMAKE_CURRENT_BINARY_DIR}/test_fourcc)

add_executable(test_config test_config.c)
target_include_directories(test_config PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_config PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_config ${CMAKE_CURRENT_BINARY_DIR}/test_config)

add_executable(test_mediaio test_mediaio.c)
target_include_directories(test_mediaio PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_mediaio PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_mediaio ${CMAKE_CURRENT_BINARY_DIR}/test_mediaio)

add_executable(test_data test_data.c)
target_include_directories(test_data PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_data PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_data ${CMAKE_CURRENT_BINARY_DIR}/test_data)

add_executable(test_callback test_callback.c)
target_include_directories(test_callback PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_callback PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_callback ${CMAKE_CURRENT_BINARY_DIR}/test_callback)

add_executable(test_misc test_misc.c)
target_include_directories(test_misc PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_misc PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_misc ${CMAKE_CURRENT_BINARY_DIR}/test_misc)

add_executable(test_graphics test_graphics.c)
target_include_directories(test_graphics PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_graphics PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_graphics ${CMAKE_CURRENT_BINARY_DIR}/test_graphics)

add_executable(test_obshpp test_obshpp.cpp)
target_include_directories(test_obshpp PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(test_obshpp PRIVATE OBS::libobs ${CMOCKA_LIBRARIES})
add_test(test_obshpp ${CMAKE_CURRENT_BINARY_DIR}/test_obshpp)
