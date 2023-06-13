cmake_minimum_required(VERSION 3.25)

project(obs-studio-test-extras)
enable_testing()

add_compile_options(-coverage)
add_link_options(-coverage)

find_package(libobs REQUIRED)
find_package(obs-frontend-api REQUIRED)

add_executable(test-crash test-crash.c)
target_link_libraries(test-crash OBS::libobs)

add_test(NAME test-crash COMMAND ./test-crash)
set_property(TEST test-crash PROPERTY PASS_REGULAR_EXPRESSION "^Testing bcrash.")

add_test(NAME test-crash-handler COMMAND ./test-crash base_set_crash_handler)
set_property(TEST test-crash-handler PROPERTY PASS_REGULAR_EXPRESSION "^In crash_handler: Testing bcrash.")

add_test(NAME test-crash-crash COMMAND ./test-crash crash-crash)
set_property(TEST test-crash-crash PROPERTY PASS_REGULAR_EXPRESSION "^Crashed in the crash handler")

add_executable(test-bmem test-bmem.c)
target_link_libraries(test-bmem OBS::libobs)

add_test(NAME test-bmem-bmalloc-0 COMMAND ./test-bmem bmalloc-0)
set_property(TEST test-bmem-bmalloc-0 PROPERTY PASS_REGULAR_EXPRESSION "Allocating 0 bytes is broken behavior")

add_test(NAME test-bmem-bmalloc-large COMMAND ./test-bmem bmalloc-large)
set_property(TEST test-bmem-bmalloc-large PROPERTY PASS_REGULAR_EXPRESSION "Out of memory while trying to allocate")

add_test(NAME test-bmem-brealloc-0 COMMAND ./test-bmem brealloc-0)
set_property(TEST test-bmem-brealloc-0 PROPERTY PASS_REGULAR_EXPRESSION "Allocating 0 bytes is broken behavior")

add_test(NAME test-bmem-brealloc-large COMMAND ./test-bmem brealloc-large)
set_property(TEST test-bmem-brealloc-large PROPERTY PASS_REGULAR_EXPRESSION "Out of memory while trying to allocate")

add_executable(list-plugins list-plugins.c module_has_qt.c)
target_link_libraries(list-plugins OBS::libobs)
add_test(NAME list-plugins COMMAND ./list-plugins)

add_subdirectory(cmocka)
