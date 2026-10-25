#ifndef PMI_FILTERS_H
#define PMI_FILTERS_H

#include <stddef.h>

int bilateral_filter(
    const double *data,  // Input image
    size_t nx,           // Number of pixels in the x-direction.
    size_t ny,           // Number of pixels in the y-direction.
    double sigma_x,      // Spatial SD in x, expressed in pixels.
    double sigma_y,      // Spatial SD in y, expressed in pixels.
    double sigma_r,      // SD for the range, expressed in sample values.
    double *result       // Output image with nx * ny elements.
);

#endif
