cmake_minimum_required(VERSION 3.16)
project(orders-cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

add_library(pricing src/pricing.cpp src/pricing.hpp src/router.cpp src/router.hpp)
target_include_directories(pricing PUBLIC src)

add_executable(orders-cpp src/main.cpp)
target_link_libraries(orders-cpp PRIVATE pricing)

enable_testing()
add_executable(test-pricing tests/test_pricing.cpp)
target_link_libraries(test-pricing PRIVATE pricing)
add_test(NAME pricing COMMAND test-pricing)

add_executable(test-router tests/test_router.cpp)
target_link_libraries(test-router PRIVATE pricing)
add_test(NAME router COMMAND test-router)
