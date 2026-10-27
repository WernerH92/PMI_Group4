int add_sphere(
    double *data, // Pointer to the input array.
    size_t nx, // Number of pixels in the x-dimension.
    size_t ny, // Number of pixels in the y-dimension.
    size_t nz, // Number of pixels in the z-dimension.
    double spacx, // Spacing in x in mm.
    double spacy, // Spacing in y in mm.
    double spacz, // Spacing in z in mm.
    double radius, // Radius in mm.
    double value // Value to add.
)
{
    if (nz == 0){
        // Define the centre pixel
        double x_0 = (nx * spacx) / 2.0f
        double y_0 = (ny * spacy) / 2.0f

        for (int x = 0; x < nx * spacx; x++){
            for (int y = 0; y < ny * spacy; y++){
                float dx = (float)x - x_0
                float dy = (float)y - y_0

                // Define the Euclidean squared and compare to the radius squared
                euclidean_squared = (dx * dx) + (dy * dy)

                    if (euclidean_squared <= (radius * radius) {
                        data[x,y] += value
                        }
            }
        }
    }





    else {
        // Define the centre voxel
        double x_0 = (nx * spacx) / 2.0f
        double y_0 = (ny * spacy) / 2.0f
        double z_0 = (nz * spacz) / 2.0f

        for (int z = 0; z < nz * spacz; z++){
            for (int y = 0; y < ny * spacy; y++){
                for (int x = 0; x < nx * spacx; x++){
                    float euclidean = }}}}
}