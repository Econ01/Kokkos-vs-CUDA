cmake_minimum_required(VERSION 3.25)

project(
    KokkosVsCUDA
    VERSION 0.1.0
    DESCRIPTION "Reproducible Kokkos and native CUDA kernel comparisons"
    LANGUAGES CXX
)

option(KVC_ENABLE_CUDA "Enable native CUDA and Kokkos CUDA targets" OFF)

if(CMAKE_EXPORT_COMPILE_COMMANDS)
    message(STATUS "Compile commands export enabled")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CUDA_STANDARD 20)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_EXTENSIONS OFF)

if(KVC_ENABLE_CUDA)
    enable_language(CUDA)

    if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
        set(CMAKE_CUDA_ARCHITECTURES "89" CACHE STRING "Target CUDA architectures")
    endif()
endif()

include(CTest)

# Smoke targets are added during Phases 3-5. Benchmark-kernel targets are added
# only after the pre-STREAM readiness gate in docs/PIPELINE.md has passed.
