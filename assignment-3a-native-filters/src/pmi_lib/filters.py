import ctypes
import math
import platform
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

from pmi_lib.image import Image


_library_name = "pmi" if platform.system() == "Windows" else "libpmi" # check to ensure the right platform
_lib = np.ctypeslib.load_library(_library_name, Path(__file__).parent) # load in C library

_double_pointer = ctypes.POINTER(ctypes.c_double)
_lib.bilateral_filter.argtypes = [
    _double_pointer,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    _double_pointer,
]
_lib.bilateral_filter.restype = ctypes.c_int


def _prepare_bilateral_filter_input(image: Image, sigma_s: float, sigma_r: float,) -> tuple[np.ndarray, float, float, float]:
    """Function to validate a 2D image and convert the spatial SD from mm to pixels. It's easiest to
    use a helper function for this before defining the main bilateral filter."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    data = np.asarray(image, dtype=np.float64)
    if data.ndim != 2:
        raise ValueError("bilateral_filter requires a 2D Image")
    if 0 in data.shape:
        raise ValueError("bilateral_filter requires an image with non-empty dimensions")

    sigma_s = float(sigma_s)
    sigma_r = float(sigma_r)
    if not math.isfinite(sigma_s) or sigma_s <= 0.0:
        raise ValueError("sigma_s must be a positive, finite value in millimeters")
    if not math.isfinite(sigma_r) or sigma_r <= 0.0:
        raise ValueError("sigma_r must be a positive, finite value")

    spacing_y, spacing_x = image.spacing
    if not all(math.isfinite(spacing) and spacing > 0.0 for spacing in image.spacing):
        raise ValueError("image spacing must contain positive, finite values")

    return data, sigma_s / spacing_x, sigma_s / spacing_y, sigma_r


def bilateral_filter_py(image: Image, sigma_s: float, sigma_r: float,) -> Image:
    """Function to apply a 2D bilateral filter implemented with Python loops.

    ``sigma_s`` is given in millimeters and is converted to horizontal and
    vertical pixels using the image spacing. ``sigma_r`` is expressed in
    image sample value units.
    """
    data, sigma_x, sigma_y, sigma_r = _prepare_bilateral_filter_input(image, sigma_s, sigma_r,) # use helper function
    result = np.zeros_like(data)

    # The local kernel extends to at least three spatial SDs in each direction.
    kernel_size_x = math.ceil(3.0 * sigma_x)
    kernel_size_y = math.ceil(3.0 * sigma_y)
    ny, nx = data.shape

    # Same loop logic, now applied to 2D.
    for y in range(ny):
        y_start = max(y - kernel_size_y, 0)
        y_end = min(y + kernel_size_y, ny - 1)

        for x in range(nx):
            x_start = max(x - kernel_size_x, 0)
            x_end = min(x + kernel_size_x, nx - 1)
            weight_sum = 0.0  # Normalize the weighted average after visiting neighbours.

            for ky in range(y_start, y_end + 1):
                for kx in range(x_start, x_end + 1):
                    dx = x - kx
                    dy = y - ky
                    difference = data[y, x] - data[ky, kx]

                    weight_s = np.exp(
                        -(
                            dx**2 / (2.0 * sigma_x**2)
                            + dy**2 / (2.0 * sigma_y**2)
                        )
                    )
                    weight_r = np.exp(-difference**2 / (2.0 * sigma_r**2))
                    weight = weight_s * weight_r

                    result[y, x] += weight * data[ky, kx]
                    weight_sum += weight

            result[y, x] /= weight_sum

    return Image(result, image.spacing)


def bilateral_filter(image: Image, sigma_s: float, sigma_r: float,) -> Image:
    """Function to apply the compiled 2D bilateral filter to an Image."""
    data, sigma_x, sigma_y, sigma_r = _prepare_bilateral_filter_input(image, sigma_s, sigma_r,)
    data = np.ascontiguousarray(data, dtype=np.float64)
    result = np.empty_like(data)

    status = _lib.bilateral_filter( # use the compiled bilateral filter written in C
        data.ctypes.data_as(_double_pointer),
        data.shape[1],
        data.shape[0],
        sigma_x,
        sigma_y,
        sigma_r,
        result.ctypes.data_as(_double_pointer),
    )
    if status != 0:
        raise ValueError(f"bilateral_filter failed with C status code {status}")

    return Image(result, image.spacing)


def masked_gaussian_filter(
    image: Image,
    mask: Image | np.ndarray,
    sigma: tuple[float, ...],
) -> Image:
    """Applies a masked Gaussian filter to an Image.
    
    `sigma` is given in millimeters and converted to pixels using image spacing.
    """
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    image_array = np.array(image, dtype=np.float32)

    if isinstance(mask, Image):
        mask_array = np.array(mask, dtype=np.float32)
    elif isinstance(mask, np.ndarray):
        mask_array = mask.astype(np.float32)
    else:
        raise TypeError("mask must be an Image or numpy array")

    if len(sigma) != image_array.ndim:
        raise ValueError("sigma length must match the dimensionality of the image")

    # Convert sigma from physical units (mm) to voxel/pixel units using spacing
    sigma_pixels = tuple(s / sp for s, sp in zip(sigma, image.spacing))

    gauss_masked_image = gaussian_filter(image_array * mask_array, sigma=sigma_pixels)
    gauss_mask = gaussian_filter(mask_array, sigma=sigma_pixels)

    with np.errstate(divide="ignore", invalid="ignore"):
        masked_gauss_filtered_image = mask_array * (gauss_masked_image / gauss_mask)

    result_array = np.nan_to_num(masked_gauss_filtered_image)
    return Image(result_array, image.spacing)
