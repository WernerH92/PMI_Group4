"""Demonstrations requested by the Assignment 3A PDF."""

import numpy as np

from .filters import bilateral_filter, bilateral_filter_py
from .image import Image
from .spheres import add_sphere, add_sphere_np, add_sphere_py


def test_filters() -> None:
    """Print the mean squared difference between the Python and C filters."""
    noise = np.random.randn(50, 100)
    image = Image(noise, spacing=(1.0, 2.0))
    add_sphere(image, radius=30.0, value=10.0)

    result_py = bilateral_filter_py(image, sigma_s=5.0, sigma_r=2.0)
    result_c = bilateral_filter(image, sigma_s=5.0, sigma_r=2.0)
    mean_squared_difference = np.mean(
        (np.asarray(result_py) - np.asarray(result_c)) ** 2
    )
    print(f"Mean squared difference: {mean_squared_difference}")


def test_spheres() -> None:
    """Print pairwise differences between Python, NumPy, and C spheres."""
    # Array and spacing axes use the same (z, y, x) order.
    shape = (9, 17, 21)
    spacing = (2.5, 1.25, 0.75)
    spheres = ((2.5, 3.0), (4.0, -1.5), (3.0, 2.0))
    implementations = (add_sphere_py, add_sphere_np, add_sphere)
    images = [
        Image(np.zeros(shape, dtype=np.float64), spacing=spacing)
        for _ in implementations
    ]

    for image, implementation in zip(images, implementations):
        for radius, value in spheres:
            implementation(image, radius=radius, value=value)

    pairs = (
        ("Python / NumPy", images[0], images[1]),
        ("Python / C", images[0], images[2]),
        ("NumPy / C", images[1], images[2]),
    )
    for label, first, second in pairs:
        mean_squared_difference = np.mean(
            (np.asarray(first) - np.asarray(second)) ** 2
        )
        print(f"Mean squared difference ({label}): {mean_squared_difference}")
