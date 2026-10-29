#include "spheres.h"

#include <math.h>
#include <stddef.h>

/* See spheres.h for information on the function inputs, array order, and return value. */
int add_sphere(
    double *data,
    const size_t nx,
    const size_t ny,
    const size_t nz,
    const double spacing_x,
    const double spacing_y,
    const double spacing_z,
    const double radius,
    const double value
) {
    /* Reject data that C cannot safely process. */
    if (
        data == NULL || nx == 0 || ny == 0 || nz == 0 ||
        !isfinite(spacing_x) || !isfinite(spacing_y) || !isfinite(spacing_z) ||
        spacing_x <= 0.0 || spacing_y <= 0.0 || spacing_z <= 0.0 ||
        !isfinite(radius) || radius < 0.0 || !isfinite(value)
    ) {
        return -1;
    }

    /* Coordinates are measured from the geometric centre of the image, which we can calculate directly since
    it is symmetrical */
    const double center_x = ((double)nx - 1.0) / 2.0;
    const double center_y = ((double)ny - 1.0) / 2.0;
    const double center_z = ((double)nz - 1.0) / 2.0;
    const double radius_squared = radius * radius;

    for (size_t z = 0; z < nz; z++) {
        /* Data has to be cast first: subtracting unsigned size_t values could lead to underflow. */
        const double dz = ((double)z - center_z) * spacing_z;

        for (size_t y = 0; y < ny; y++) {
            const double dy = ((double)y - center_y) * spacing_y;

            for (size_t x = 0; x < nx; x++) {
                const double dx = ((double)x - center_x) * spacing_x;
                const double distance_squared = dx * dx + dy * dy + dz * dz;

                if (distance_squared <= radius_squared) {
                    /* Flatten (z, y, x) to the matching C memory position. */
                    const size_t index = (z * ny + y) * nx + x;
                    data[index] += value;
                }
            }
        }
    }

    return 0;
}
