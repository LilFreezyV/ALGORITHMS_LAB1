cmake_minimum_required(VERSION 3.14)
project(ALGORYTHMS_LAB1 CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================
# 1. Библиотека алгоритмов
# ============================================================
add_library(algorithms STATIC
        src/two_pointers.cpp
        src/binary_search.cpp
        src/exponential.cpp
        src/double_binary.cpp
)

# Путь к заголовочным файлам (PUBLIC = доступен всем, кто линкует algorithms)
target_include_directories(algorithms PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

# ============================================================
# 2. GoogleTest через FetchContent
# ============================================================
include(FetchContent)

FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

# Обязательно для Windows, иначе ошибки линковки CRT
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(googletest)

enable_testing()

# ============================================================
# 3. Тесты
# ============================================================
add_executable(tests tests/test_algos.cpp)
target_link_libraries(tests PRIVATE algorithms GTest::gtest_main)
add_test(NAME all_tests COMMAND tests)

# ============================================================
# 4. Бенчмарк (замеры имеют смысл только в Release-сборке)
# ============================================================
add_executable(bench bench/bench.cpp)
target_link_libraries(bench PRIVATE algorithms)