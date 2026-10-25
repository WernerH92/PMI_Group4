#include "filters.h"

#include <math.h>
#include <stddef.h>


// Applies a 2-dimensional bilateral filter and returns 0 on success. Extended from the 1D example
// in the course.
int bilateral_filter(
    const double *data,
    const size_t nx,
    const size_t ny,
    const double sigma_x,
    const double sigma_y,
    const double sigma_r,
    double *result
) { // Checks to ensure that the required sigmas are positive and data actually exists
    if (
        data == NULL || result == NULL || nx == 0 || ny == 0 ||
        sigma_x <= 0.0 || sigma_y <= 0.0 || sigma_r <= 0.0
    ) {
        return -1;
    }

    // The local kernel extends to at least three spatial SDs in two directions now.
    const size_t kernel_size_x = (size_t)ceil(3.0 * sigma_x);
    const size_t kernel_size_y = (size_t)ceil(3.0 * sigma_y);
    // The logic of the loops are essentially the same, but now they extend in two directions instead of one.
    for (size_t y = 0; y < ny; y++) {
        const size_t y_start = y > kernel_size_y ? y - kernel_size_y : 0;
        const size_t y_end = kernel_size_y > ny - 1 - y ? ny - 1 : y + kernel_size_y;

        for (size_t x = 0; x < nx; x++) {
            const size_t x_start = x > kernel_size_x ? x - kernel_size_x : 0;
            const size_t x_end = kernel_size_x > nx - 1 - x ? nx - 1 : x + kernel_size_x;
            const size_t index = y * nx + x;
            double weight_sum = 0.0;

            result[index] = 0.0;

            for (size_t ky = y_start; ky <= y_end; ky++) {
                for (size_t kx = x_start; kx <= x_end; kx++) {
                    const size_t neighbor_index = ky * nx + kx;
                    // Cast before subtraction: size_t is unsigned and could underflow.
                    const double dx = (double)x - (double)kx;
                    const double dy = (double)y - (double)ky;
                    const double difference = data[index] - data[neighbor_index];
                    const double weight_s = exp(
                        -(
                            (dx * dx) / (2.0 * sigma_x * sigma_x) +
                            (dy * dy) / (2.0 * sigma_y * sigma_y)
                        )
                    );
                    const double weight_r = exp(
                        -(difference * difference) / (2.0 * sigma_r * sigma_r)
                    );
                    const double weight = weight_s * weight_r;

                    result[index] += weight * data[neighbor_index];
                    weight_sum += weight;
                }
            }

            result[index] /= weight_sum;
        }
    }

    return 0;
}
