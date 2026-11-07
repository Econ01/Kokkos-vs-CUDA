add_executable(kokkos_smoke kokkos_smoke.cpp)
target_link_libraries(kokkos_smoke PRIVATE Kokkos::kokkos)

add_test(NAME kokkos_smoke COMMAND kokkos_smoke)
set_tests_properties(kokkos_smoke PROPERTIES LABELS "smoke;kokkos")
