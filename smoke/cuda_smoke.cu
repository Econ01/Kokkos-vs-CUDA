#include <cuda_runtime.h>
#include <iostream>
#include <cstdio>
#include <cstddef>
#include <vector>

__global__ void kernel_write(int* values, int numElements){
    const int global_index = blockIdx.x * blockDim.x + threadIdx.x;

    if (global_index < numElements){
        values[global_index] = 2 * global_index;
    }
}

constexpr int element_count = 256;
constexpr int threads_per_block = 128;
constexpr std::size_t bytes = element_count * sizeof(int);
constexpr int blocks = (element_count + threads_per_block - 1) / threads_per_block;

int main(void){
    int device_count = 0;
    cudaError_t err = cudaGetDeviceCount(&device_count);

    // Checking for available CUDA devices.
    if (err != cudaSuccess) {
        fprintf(stderr, "No CUDA capable device was found: %s\n", cudaGetErrorString(err));
        return 1;
    } else {
        printf("Number of CUDA devices: %d\n", device_count);
    }

    // Raising an error in case system detects CUDA but there are no available devices.
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

    // Raising error if the CUDA compute capability is no 8.9 (Development machine).
    if (properties.major != 8 || properties.minor != 9){
        printf("Detected compute capability does not match with requirements.\n");
        printf("Detected compute capability: %d.%d\n", properties.major, properties.minor);
        printf("Required compute capability: 8.9\n");
        return 1;
    }

    printf("Device Name: %s\n", properties.name);
    printf("Total Global Memory: %zu MB\n", properties.totalGlobalMem / (1024 * 1024));
    printf("Compute Capability: %d.%d\n", properties.major, properties.minor);

    int* device_values = nullptr;
    std::vector<int> host_values(element_count);

    // Allocating device buffer.
    err = cudaMalloc(reinterpret_cast<void**>(&device_values), bytes);
    if (err != cudaSuccess) {
        fprintf(stderr, "Couldn't allocate device buffer: %s\n", cudaGetErrorString(err));
        return 1;
    } else {
        printf("Allocated device buffer.\n");
    }

    // Launching two blocks with threads_per_block threads each,
    // giving one thread for each of the element_count elements.
    kernel_write<<<blocks, threads_per_block>>>(
        device_values,
        element_count
    );

    err = cudaGetLastError();
    if (err != cudaSuccess) {
        fprintf(stderr, "Kernel launch failed: %s\n", cudaGetErrorString(err));
        cudaFree(device_values);
        return 1;
    } else {
        printf("Kernel launched.\n");
    }

    err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {
        fprintf(stderr, "CUDA device synchronization failed: %s\n", cudaGetErrorString(err));
        cudaFree(device_values);
        return 1;
    } else {
        printf("CUDA device synchronized.\n");
    }

    err = cudaGetLastError();
    if (err != cudaSuccess) {
        fprintf(stderr, "Error encountered: %s\n", cudaGetErrorString(err));
        cudaFree(device_values);
        return 1;
    }

    err = cudaMemcpy(
        host_values.data(),
        device_values,
        bytes,
        cudaMemcpyDeviceToHost
    );

    if (err != cudaSuccess) {
        fprintf(stderr, "Memory copy failed: %s\n", cudaGetErrorString(err));
        cudaFree(device_values);
        return 1;
    } else {
        printf("Device memory copied to host successfully.\n");
    }

    bool valid = true;

    for (int index = 0; index < element_count; ++index) {
        const int expected = 2 * index;

        if (host_values[index] != expected) {
            fprintf(
                stderr,
                "Validation failed at index %d: expected %d, got %d\n",
                index,
                expected,
                host_values[index]
            );
            valid = false;
            break;
        }
    }

    if (valid == false) {
        cudaFree(device_values);
        return 1;
    }

    printf("Validated all %d values successfully.\n", element_count);

    err = cudaFree(device_values);
    if (err != cudaSuccess) {
        fprintf(stderr, "Failed to free device buffer: %s\n", cudaGetErrorString(err));
        return 1;
    }

    device_values = nullptr;

    return 0;
}