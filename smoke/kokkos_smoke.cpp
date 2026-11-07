#include <Kokkos_Core.hpp>

#include <iostream>

int main(int argc, char* argv[]) {
    constexpr int element_count = 257;
    double sum = 0.0;
    bool passed = true;

    {
        Kokkos::ScopeGuard guard(argc, argv);

        if (!Kokkos::is_initialized()) {
            std::cerr << "Kokkos failed to initialize\n";
            passed = false;
        }

        Kokkos::print_configuration(std::cout);

        Kokkos::View<double*> values("values", element_count);
        Kokkos::parallel_for(
            "fill_values",
            element_count,
            KOKKOS_LAMBDA(const int index) {
                values(index) = 2.0 * static_cast<double>(index);
            }
        );

        Kokkos::parallel_reduce(
            "sum_values",
            element_count,
            KOKKOS_LAMBDA(const int index, double& partial_sum) {
                partial_sum += values(index);
            },
            sum
        );
        Kokkos::fence();

        auto host_values = Kokkos::create_mirror_view(values);
        Kokkos::deep_copy(host_values, values);

        for (int index = 0; index < element_count; ++index) {
            const double expected = 2.0 * static_cast<double>(index);
            if (host_values(index) != expected) {
                std::cerr << "Value mismatch at index " << index << ": expected "
                          << expected << ", got " << host_values(index) << '\n';
                passed = false;
                break;
            }
        }

        const double expected_sum =
            static_cast<double>(element_count) * static_cast<double>(element_count - 1);
        if (sum != expected_sum) {
            std::cerr << "Reduction mismatch: expected " << expected_sum << ", got " << sum << '\n';
            passed = false;
        }

        std::cout << "Validated " << element_count << " values; reduction = " << sum << '\n';
    }

    if (!Kokkos::is_finalized()) {
        std::cerr << "Kokkos failed to finalize\n";
        return 2;
    }
    if (!passed) {
        return 1;
    }

    std::cout << "Kokkos initialization, parallel execution, reduction, and finalization passed\n";
    return 0;
}
