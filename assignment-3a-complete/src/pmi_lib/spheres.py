"""Python script that creates and compares various circles and spheres with three different implementations.
These are normal Python loops, numpy functions and a C algorithm."""

import ctypes
import math
import platform
from pathlib import Path

import numpy as np

from .image import Image

# Linux / macos compatibility check
_LIBRARY_NAME = "pmi" if platform.system() == "Windows" else "libpmi"

# numpy automatically chooses the correct library suffix (.dll, .so, or .dylib).
_LIBRARY = np.ctypeslib.load_library(_LIBRARY_NAME, Path(__file__).parent)
_DOUBLE_POINTER = ctypes.POINTER(ctypes.c_double)

_LIBRARY.add_sphere.argtypes = [
    _DOUBLE_POINTER,  # Pixel data: double *
    ctypes.c_size_t,  # Number of x samples
    ctypes.c_size_t,  # Number of y samples
    ctypes.c_size_t,  # Number of z samples
    ctypes.c_double,  # Spacing in x (mm)
    ctypes.c_double,  # Spacing in y (mm)
    ctypes.c_double,  # Spacing in z (mm)
    ctypes.c_double,  # Sphere radius (mm)
    ctypes.c_double,  # Value to add
]
_LIBRARY.add_sphere.restype = ctypes.c_int


def _prepare_sphere_input(image: Image, radius: float, value: float,) -> tuple[np.ndarray, tuple[float, float, float], float, float]:
    """Function to check image input format and to return data and spacing in ``(z, y, x)`` order."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    # A 1D line becomes one row, a 2D image becomes one z slice.
    if image._data.ndim not in (1, 2, 3):
        raise ValueError("add_sphere supports only 1D, 2D, and 3D images")
    if 0 in image._data.shape:
        raise ValueError("add_sphere requires non-empty image dimensions")

    # The C function only accepts real numeric values, not strings, booleans, or complex data.
    is_real_numeric = np.issubdtype(image._data.dtype, np.number)
    if not is_real_numeric or np.iscomplexobj(image._data):
        raise TypeError("image data must have a real numeric data type")
    has_valid_spacing = all(math.isfinite(spacing) and spacing > 0.0 for spacing in image.spacing)
    if not has_valid_spacing:
        raise ValueError("image spacing must contain positive, finite values")

    # Similar checks for the radius of the circle and value
    try:
        radius = float(radius)
        value = float(value)
    except (TypeError, ValueError) as error:
        raise TypeError("radius and value must be real numbers") from error

    if not math.isfinite(radius) or radius < 0.0:
        raise ValueError("radius must be a non negative, finite value in millimetres")
    if not math.isfinite(value):
        raise ValueError("value must be finite")

    # C requires data to be stored contiguously in memory for speed and comparibility as explained in the book.
    # Using the same data for all three versions lets their results be compared fairly.
    data = np.ascontiguousarray(image._data, dtype=np.float64)

    # Add any potential missing leading dimensions so every image can use the same z-y-x coordinates.
    if data.ndim == 1:
        spacing_zyx = (1.0, 1.0, float(image.spacing[0]))
    elif data.ndim == 2:
        spacing_zyx = (1.0, float(image.spacing[0]), float(image.spacing[1]))
    else:
        spacing_zyx = (
            float(image.spacing[0]),
            float(image.spacing[1]),
            float(image.spacing[2]),
        )

    return data, spacing_zyx, radius, value


def _as_3d_view(data: np.ndarray) -> np.ndarray:
    """Add leading dimensions until ``data`` has ``(z, y, x)`` axes."""
    while data.ndim < 3:
        # np.newaxis creates a view, so the original data is not copied here!
        data = data[np.newaxis, :]
    return data


def add_sphere_py(image: Image, radius: float, value: float = 1.0) -> None:
    """Function that adds a circle or sphere using ordinary Python loops."""
    data, spacing_zyx, radius, value = _prepare_sphere_input(image, radius, value)
    view = _as_3d_view(data)
    spacing_z, spacing_y, spacing_x = spacing_zyx
    nz, ny, nx = view.shape

    # The centre lies halfway between the two central points for even sizes.
    center_z = (nz - 1.0) / 2.0
    center_y = (ny - 1.0) / 2.0
    center_x = (nx - 1.0) / 2.0
    radius_squared = radius * radius

    for z in range(nz):
        dz = (z - center_z) * spacing_z
        for y in range(ny):
            dy = (y - center_y) * spacing_y
            for x in range(nx):
                dx = (x - center_x) * spacing_x
                distance_squared = dx * dx + dy * dy + dz * dz

                if distance_squared <= radius_squared:
                    view[z, y, x] += value

    # Store data because ascontiguousarray may have created a separate copy.
    image._data = data


def add_sphere_np(image: Image, radius: float, value: float = 1.0) -> None:
    """Function that adds a circle or sphere using NumPy array operations."""
    data, spacing_zyx, radius, value = _prepare_sphere_input(image, radius, value)
    view = _as_3d_view(data)
    spacing_z, spacing_y, spacing_x = spacing_zyx
    nz, ny, nx = view.shape
    center_z = (nz - 1.0) / 2.0
    center_y = (ny - 1.0) / 2.0
    center_x = (nx - 1.0) / 2.0

    # np.indices gives the z, y, and x coordinate of every sample at once.
    z, y, x = np.indices(view.shape, dtype=np.float64)
    distance_squared = (
        ((x - center_x) * spacing_x) ** 2
        + ((y - center_y) * spacing_y) ** 2
        + ((z - center_z) * spacing_z) ** 2
    )
    view[distance_squared <= radius * radius] += value

    # Store data because ascontiguousarray may have created a separate copy.
    image._data = data


def add_sphere(image: Image, radius: float, value: float = 1.0) -> None:
    """Function that adds a circle or sphere with the compiled C function."""
    data, spacing_zyx, radius, value = _prepare_sphere_input(image, radius, value)
    view = _as_3d_view(data)
    spacing_z, spacing_y, spacing_x = spacing_zyx
    nz, ny, nx = view.shape

    status = _LIBRARY.add_sphere(
        view.ctypes.data_as(_DOUBLE_POINTER),
        nx,
        ny,
        nz,
        spacing_x,
        spacing_y,
        spacing_z,
        radius,
        value,
    )
    if status != 0:
        raise ValueError(f"add_sphere failed with C status code {status}")

    # Store data because ascontiguousarray may have created a separate copy.
    image._data = data
