#include <cuda_runtime.h>
#include <iostream>
#include <cstdio>

int main(void){
    int device_count = 0;
    cudaError_t err = cudaGetDeviceCount(&device_count);

    if (err != cudaSuccess) {
        fprintf(stderr, "No CUDA capable device was found: %s\n", cudaGetErrorString(err));
        return 1;
    } else {
        printf("Number of CUDA devices: %d\n", device_count);
    }

    if (device_count == 0) {
        fprintf(stderr, "No CUDA-capable device was found.\n");
        return 1;
    }

    err = cudaSetDevice(0);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error encountered while setting CUDA device: %s\n", cudaGetErrorString(err));
        return 1;
    } else {
        printf("CUDA device successfully set.\n");
    }
    
    cudaDeviceProp properties{};
    err = cudaGetDeviceProperties(&properties, 0);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error getting properties: %s\n", cudaGetErrorString(err));
        return 1;
    }

    if (properties.major != 8 || properties.minor != 9){
        printf("Detected compute capability does not match with requirements.");
        printf("Detected compute capability: %d.%d\n", properties.major, properties.minor);
        printf("Required compute capability: 8.9");
        return 1;
    }

    printf("Device Name: %s\n", properties.name);
    printf("Total Global Memory: %zu MB\n", properties.totalGlobalMem / (1024 * 1024));
    printf("Compute Capability: %d.%d\n", properties.major, properties.minor);

    return 0;
}