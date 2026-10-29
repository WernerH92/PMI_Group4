#ifndef PMI_SPHERES_H
#define PMI_SPHERES_H

#include <stddef.h>

/*
 * Header file that defines the add_sphere function made in C. Data must be a contiguous array with shape (nz, ny, nx).
 * Spacing and radius values are expressed in millimetres.
 * Returns 0 on success and -1 when an argument is invalid.
 */
int add_sphere(
    double *data,
    size_t nx,
    size_t ny,
    size_t nz,
    double spacing_x,
    double spacing_y,
    double spacing_z,
    double radius,
    double value
);

#endif
