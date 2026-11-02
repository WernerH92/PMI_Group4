#include "filters.h"

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>


/*
 * Apply a 2D bilateral filter.
 * Return 0 on success, -1 when an argument is invalid, or -2 when a lookup
 * table cannot be allocated.
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
        !isfinite(sigma_x) || !isfinite(sigma_y) || !isfinite(sigma_r) ||
        sigma_x <= 0.0 || sigma_y <= 0.0 || sigma_r <= 0.0
    ) {
        return -1;
    }

    /* Use samples within three spatial standard deviations of each pixel. */
    const double maximum_sigma = ((double)(SIZE_MAX - 1)) / 3.0;
    if (sigma_x > maximum_sigma || sigma_y > maximum_sigma) {
        return -1;
    }

    const size_t kernel_size_x = (size_t)ceil(3.0 * sigma_x);
    const size_t kernel_size_y = (size_t)ceil(3.0 * sigma_y);
    if (
        kernel_size_x > SIZE_MAX / sizeof(double) - 1 ||
        kernel_size_y > SIZE_MAX / sizeof(double) - 1
    ) {
        return -1;
    }

    const size_t table_size_x = kernel_size_x + 1;
    const size_t table_size_y = kernel_size_y + 1;
    double *spatial_weights_x = malloc(table_size_x * sizeof(*spatial_weights_x));
    double *spatial_weights_y = malloc(table_size_y * sizeof(*spatial_weights_y));
    if (spatial_weights_x == NULL || spatial_weights_y == NULL) {
        free(spatial_weights_x);
        free(spatial_weights_y);
        return -2;
    }

    /* The spatial Gaussian is separable into independent x and y weights. */
    const double spatial_scale_x = -1.0 / (2.0 * sigma_x * sigma_x);
    const double spatial_scale_y = -1.0 / (2.0 * sigma_y * sigma_y);
    for (size_t distance = 0; distance <= kernel_size_x; distance++) {
        const double offset = (double)distance;
        spatial_weights_x[distance] = exp(offset * offset * spatial_scale_x);
    }
    for (size_t distance = 0; distance <= kernel_size_y; distance++) {
        const double offset = (double)distance;
        spatial_weights_y[distance] = exp(offset * offset * spatial_scale_y);
    }

    /* Keep the range Gaussian exponential, but move its division out of the loop. */
    const double range_scale = -1.0 / (2.0 * sigma_r * sigma_r);

    for (size_t y = 0; y < ny; y++) {
        const size_t y_start = y > kernel_size_y ? y - kernel_size_y : 0;
        const size_t y_end = kernel_size_y > ny - 1 - y ? ny - 1 : y + kernel_size_y;

        for (size_t x = 0; x < nx; x++) {
            const size_t x_start = x > kernel_size_x ? x - kernel_size_x : 0;
            const size_t x_end = kernel_size_x > nx - 1 - x ? nx - 1 : x + kernel_size_x;
            const size_t index = y * nx + x;
            double weight_sum = 0.0;
            double weighted_sum = 0.0;

            for (size_t ky = y_start; ky <= y_end; ky++) {
                const size_t distance_y = y > ky ? y - ky : ky - y;
                const double spatial_weight_y = spatial_weights_y[distance_y];

                for (size_t kx = x_start; kx <= x_end; kx++) {
                    const size_t neighbor_index = ky * nx + kx;
                    const size_t distance_x = x > kx ? x - kx : kx - x;
                    const double difference = data[index] - data[neighbor_index];
                    const double spatial_weight =
                        spatial_weights_x[distance_x] * spatial_weight_y;
                    const double range_weight = exp(difference * difference * range_scale);
                    const double weight = spatial_weight * range_weight;

                    weighted_sum += weight * data[neighbor_index];
                    weight_sum += weight;
                }
            }

            result[index] = weighted_sum / weight_sum;
        }
    }

    free(spatial_weights_y);
    free(spatial_weights_x);
    return 0;
}
