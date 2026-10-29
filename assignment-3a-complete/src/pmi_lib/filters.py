"""Python script that contains all of the filtering functions for Assignment 3A as well as the masked Gaussian
filter function from Assignment 2A/2B."""

import ctypes
import math
import platform
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

from .image import Image

# Linux / macos compatibility check
_LIBRARY_NAME = "pmi" if platform.system() == "Windows" else "libpmi"

# numpy automatically selects the correct library suffix (.dll, .so, or .dylib).
_LIBRARY = np.ctypeslib.load_library(_LIBRARY_NAME, Path(__file__).parent)
_DOUBLE_POINTER = ctypes.POINTER(ctypes.c_double)

_LIBRARY.bilateral_filter.argtypes = [
    _DOUBLE_POINTER,  # Input pixels: double *
    ctypes.c_size_t,  # Image width
    ctypes.c_size_t,  # Image height
    ctypes.c_double,  # Spatial standard deviation in x pixels
    ctypes.c_double,  # Spatial standard deviation in y pixels
    ctypes.c_double,  # Range standard deviation
    _DOUBLE_POINTER,  # Output pixels: double *
]
_LIBRARY.bilateral_filter.restype = ctypes.c_int


def _prepare_bilateral_filter_input(image: Image, sigma_s: float, sigma_r: float,) -> tuple[np.ndarray, float, float, float]:
    """Check the input of a 2D image and convert the spatial standard deviation to pixels."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    data = np.asarray(image._data, dtype=np.float64)
    if data.ndim != 2:
        raise ValueError("bilateral_filter requires a 2D Image")
    if 0 in data.shape:
        raise ValueError("bilateral_filter requires non empty image dimensions")

    sigma_s = float(sigma_s)
    sigma_r = float(sigma_r)
    if not math.isfinite(sigma_s) or sigma_s <= 0.0:
        raise ValueError("sigma_s must be a positive, finite value in millimetres")
    if not math.isfinite(sigma_r) or sigma_r <= 0.0:
        raise ValueError("sigma_r must be a positive, finite value")

    spacing_y, spacing_x = image.spacing
    if not all(math.isfinite(spacing) and spacing > 0.0 for spacing in image.spacing):
        raise ValueError("image spacing must contain positive, finite values")

    # sigma_s is supplied in millimetres, but both algorithms use pixel distance.
    sigma_x = sigma_s / spacing_x
    sigma_y = sigma_s / spacing_y
    return data, sigma_x, sigma_y, sigma_r


def bilateral_filter_py(image: Image, sigma_s: float, sigma_r: float) -> Image:
    """Function that returns a 2D bilateral filtered copy of ``image`` using Python loops."""
    data, sigma_x, sigma_y, sigma_r = _prepare_bilateral_filter_input(image, sigma_s, sigma_r,)
    result = np.zeros_like(data)

    # A radius of three standard deviations covers nearly all Gaussian weights.
    radius_x = math.ceil(3.0 * sigma_x)
    radius_y = math.ceil(3.0 * sigma_y)
    ny, nx = data.shape

    for y in range(ny):
        y_start = max(y - radius_y, 0)
        y_end = min(y + radius_y, ny - 1)

        for x in range(nx):
            x_start = max(x - radius_x, 0)
            x_end = min(x + radius_x, nx - 1)
            weight_sum = 0.0

            for neighbor_y in range(y_start, y_end + 1):
                for neighbor_x in range(x_start, x_end + 1):
                    dx = x - neighbor_x
                    dy = y - neighbor_y
                    intensity_difference = data[y, x] - data[neighbor_y, neighbor_x]

                    spatial_weight = np.exp(
                        -(
                            dx**2 / (2.0 * sigma_x**2)
                            + dy**2 / (2.0 * sigma_y**2)
                        )
                    )
                    range_weight = np.exp(
                        -intensity_difference**2 / (2.0 * sigma_r**2)
                    )
                    weight = spatial_weight * range_weight

                    result[y, x] += weight * data[neighbor_y, neighbor_x]
                    weight_sum += weight

            # Divide by the weights so each result is a weighted average.
            result[y, x] /= weight_sum

    return Image(result, image.spacing)


def bilateral_filter(image: Image, sigma_s: float, sigma_r: float) -> Image:
    """Function that returns a 2D bilateral filtered copy of ``image`` using compiled C."""
    data, sigma_x, sigma_y, sigma_r = _prepare_bilateral_filter_input(image, sigma_s, sigma_r,)

    # The C function needs a double pointer and assumes contiguous memory storage.
    data = np.ascontiguousarray(data, dtype=np.float64)
    result = np.empty_like(data)

    status = _LIBRARY.bilateral_filter(
        data.ctypes.data_as(_DOUBLE_POINTER),
        data.shape[1],
        data.shape[0],
        sigma_x,
        sigma_y,
        sigma_r,
        result.ctypes.data_as(_DOUBLE_POINTER),
    )
    if status != 0:
        raise ValueError(f"bilateral_filter failed with C status code {status}")

    return Image(result, image.spacing)


def masked_gaussian_filter(
    image: Image,
    mask: Image | np.ndarray,
    sigma: tuple[float, ...],
) -> Image:
    """Apply a Gaussian filter inside ``mask`` with sigma values in millimetres."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    image_data = np.asarray(image, dtype=np.float32)
    if isinstance(mask, Image):
        mask_data = np.asarray(mask, dtype=np.float32)
    elif isinstance(mask, np.ndarray):
        mask_data = mask.astype(np.float32)
    else:
        raise TypeError("mask must be an Image or NumPy array")

    if len(sigma) != image_data.ndim:
        raise ValueError("sigma length must match the dimensionality of the image")

    # scipy.ndimage expects sigma in pixels rather than millimetres.
    sigma_pixels = tuple(value / spacing for value, spacing in zip(sigma, image.spacing))
    filtered_data = gaussian_filter(image_data * mask_data, sigma=sigma_pixels)
    filtered_mask = gaussian_filter(mask_data, sigma=sigma_pixels)

    # Dividing both filtered arrays avoids darkening pixels near a mask edge.
    with np.errstate(divide="ignore", invalid="ignore"):
        result = mask_data * (filtered_data / filtered_mask)

    return Image(np.nan_to_num(result), image.spacing)
