import numpy as np
import image


def add_sphere_py(image: image.Image, radius: float, value: float = 1.0) -> None:
    '''
    For a 2D image: Draws a circle of given radius around the centre of the image. Adds value to the pixel value
    of all pixels within the circle

    For a 3D image: Draws a sphere of given radius around the centre of the 3D image array. Adds a value to the
    pixel value of all pixels within the sphere.

    :param image: Image data of the class Image. Has attributes data and spacing.
    :param radius: Radius of the circle or sphere in mm.
    :param value: Value to be added to pixels within radius.
    '''

    # Adds value to pixels of a 2D image within a circle of defined radius
    if len(np.shape(image._data)) == 2:

        # Define the centre pixel of the image
        x_length = image._data.shape[0] * image.spacing[0]
        y_length = image._data.shape[1] * image.spacing[1]

        x_0 = (x_length / 2) / image.spacing[0]
        y_0 = (y_length / 2) / image.spacing[1]

        # Identify pixels within radius using Euclidean distance
        for i in range(image._data.shape[0]):
            for j in range(image._data.shape[1]):
                euclidean_distance = np.sqrt(((x_0 - i)**2)+((y_0 - j)**2))
                if euclidean_distance <= radius:
                    image._data[i,j] += value

    # Adds value to voxels of a 3D image within a sphere of defined radius
    elif len(np.shape(image._data)) == 3:

        # Define the centre of the 3D image array
        z_length = image._data.shape[0] * image.spacing[2]
        x_length = image._data.shape[1] * image.spacing[0]
        y_length = image._data.shape[2] * image.spacing[1]

        x_0 = (x_length / 2) / image.spacing[0]
        y_0 = (y_length / 2) / image.spacing[1]
        z_0 = (z_length / 2) / image.spacing[2]

        # Identify pixels within radius using Euclidean distance
        for i in range(image._data.shape[0]):
            for j in range(image._data.shape[1]):
                for k in range(image._data.shape[2]):
                    euclidean_distance = np.sqrt(((z_0 - k)**2)+((x_0 - i)**2)+((y_0 - j)**2))
                    if euclidean_distance <= radius:
                        image._data[i,j,k] += value
