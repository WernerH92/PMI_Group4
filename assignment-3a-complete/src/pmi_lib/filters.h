#ifndef PMI_FILTERS_H
#define PMI_FILTERS_H

#include <stddef.h>

/*
 * Filter a contiguous image in C with shape (ny, nx).
 * sigma_x and sigma_y are measured in pixels. sigma_r is measured in image
 * intensity units. result must contain nx * ny double values.
 */
int bilateral_filter(
    const double *data,
    size_t nx,
    size_t ny,
    double sigma_x,
    double sigma_y,
    double sigma_r,
    double *result
);

#endif
