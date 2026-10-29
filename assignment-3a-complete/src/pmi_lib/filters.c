#include "filters.h"

#include <math.h>
#include <stddef.h>


/*
 * Apply a 2D bilateral filter.
 * Return 0 on success or -1 when an argument is invalid.
 */
int bilateral_filter(
    const double *data,
    const size_t nx,
    const size_t ny,
    const double sigma_x,
    const double sigma_y,
    const double sigma_r,
    double *result
) {
    /* C cannot raise Python exceptions, so reject any invalid input here. */
    if (
        data == NULL || result == NULL || nx == 0 || ny == 0 ||
        sigma_x <= 0.0 || sigma_y <= 0.0 || sigma_r <= 0.0
    ) {
        return -1;
    }

    /* Use samples within three spatial standard deviations of each pixel. */
    const size_t kernel_size_x = (size_t)ceil(3.0 * sigma_x);
    const size_t kernel_size_y = (size_t)ceil(3.0 * sigma_y);

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
                    /* Cast before subtraction because size_t is unsigned. */
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
