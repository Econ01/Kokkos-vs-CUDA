add_executable(kokkos_smoke kokkos_smoke.cpp)
target_link_libraries(kokkos_smoke PRIVATE Kokkos::kokkos)

add_test(NAME kokkos_smoke COMMAND kokkos_smoke)
set_tests_properties(kokkos_smoke PROPERTIES LABELS "smoke;kokkos")

if(KVC_ENABLE_CUDA)
    add_executable(cuda_smoke cuda_smoke.cu)

    set_target_properties(cuda_smoke PROPERTIES CUDA_ARCHITECTURES 89)

    add_test(NAME cuda_smoke COMMAND cuda_smoke)
    set_tests_properties(cuda_smoke PROPERTIES LABELS "smoke;cuda")
endif()