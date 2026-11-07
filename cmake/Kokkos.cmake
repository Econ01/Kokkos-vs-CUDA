include_guard(GLOBAL)

include(FetchContent)

set(Kokkos_ENABLE_SERIAL ON CACHE BOOL "Enable the Kokkos Serial host backend" FORCE)
set(Kokkos_ENABLE_TESTS OFF CACHE BOOL "Do not build upstream Kokkos tests" FORCE)
set(Kokkos_ENABLE_EXAMPLES OFF CACHE BOOL "Do not build upstream Kokkos examples" FORCE)

if(KVC_ENABLE_CUDA)
    set(Kokkos_ENABLE_CUDA ON CACHE BOOL "Enable the Kokkos CUDA backend" FORCE)
    set(Kokkos_ARCH_ADA89 ON CACHE BOOL "Target NVIDIA Ada 89" FORCE)
    set(
        Kokkos_ENABLE_COMPILE_AS_CMAKE_LANGUAGE ON
        CACHE BOOL "Compile Kokkos CUDA sources through CMake's CUDA language support"
        FORCE
    )
else()
    set(Kokkos_ENABLE_CUDA OFF CACHE BOOL "Disable the Kokkos CUDA backend" FORCE)
endif()

FetchContent_Declare(
    Kokkos
    URL "https://github.com/kokkos/kokkos/releases/download/5.2.2/kokkos-5.2.2.tar.gz"
    URL_HASH "SHA256=d6557aaef39302282a15f9c770433d1fcdf4e961dfd6d9ed726b9d0d0f546b9f"
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(Kokkos)
