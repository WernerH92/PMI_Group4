import joblib


def apply_to_slices(image: Image, function: Callable, *args, **kwargs) -> Image:
    '''
    Applies a filter to each slice in an Image object in parallel using multiprocessing.

    :param image: The Image object to be filtered.
    :param function: The fucntion to be applied to each slice.
    :param args: The arguments necessary to run function.
    :param kwargs: The kwargs necessary to run function.
    :return: Filtered Image object.
    '''

    # Use 1 fewer CPUs than available, unless only 1 CPU is available
    if joblib.cpu_count() == 1:
        cpu_count = 1
    else:
        cpu_count = joblib.cpu_count() - 1

    # Create a list consisting of the image slices
    image_slices = [Image(slice, spacing=image.spacing[:-1]) for slice in image._data]

    # Apply the callable function to each slice in parallel. Store the filtered slices in a list
    filtered_images = joblib.Parallel(n_jobs=cpu_count, prefer="threads")(
        joblib.delayed(function)(slice, *args, **kwargs) for slice in image_slices
    )

    # Return the filtered slices as an Image object
    return Image(np.array(filtered_images), spacing=image.spacing)