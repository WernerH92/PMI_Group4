def apply_to_slices(image: Image, function: Callable, *args, **kwargs) -> Image:
    '''
    Applies a filter to each slice in an Image object.

    :param image: The Image object to be filtered.
    :param function: The fucntion to be applied to each slice.
    :param args: The arguments necessary to run function.
    :param kwargs: The kwargs necessary to run function.
    :return: Filtered Image object.
    '''
    # Create a list consisting of the image slices
    image_slices = [Image(slice, spacing=image.spacing[:-1]) for slice in image._data]

    # Apply the callable function to each slice. Store the filtered slices in a list
    filtered_images = [function(slice, *args, **kwargs) for slice in image_slices]

    # Return the filtered slices as an Image object
    return Image(np.array(filtered_images), spacing=image.spacing)
