"""NIfTI reading and writing for images stored as ``(y, x)`` or ``(z, y, x)``."""

import os

import nibabel as nib
import numpy as np

from .image import Image


def _validate_dimensions(data: np.ndarray) -> None:
    if data.ndim not in (2, 3):
        raise ValueError("NIfTI data must be 2D or 3D")


def read_nifti(file_path: str | os.PathLike[str]) -> Image:
    """Read a NIfTI image and return data with matching ``(z, y, x)`` axes."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file: {file_path}")

    try:
        nifti_image = nib.load(file_path)
    except Exception as error:
        raise ValueError(f"Failed to load NIfTI file {file_path}: {error}") from error

    nifti_data = nifti_image.get_fdata()
    _validate_dimensions(nifti_data)

    # NIfTI uses (x, y[, z]); reverse the x/y flip and then reverse the axes.
    data = np.transpose(np.flip(nifti_data, axis=(0, 1)))
    spacing = tuple(
        float(value) for value in reversed(nifti_image.header.get_zooms()[:data.ndim])
    )
    return Image(data, spacing)


def write_nifti(image: Image, file_path: str | os.PathLike[str] = "out.nii.gz") -> str:
    """Write a 2D or 3D ``Image`` as a NIfTI file."""
    if not isinstance(image, Image):
        raise TypeError("image must be an instance of Image")

    data = np.array(image, copy=True)
    _validate_dimensions(data)
    if data.dtype == bool:
        data = data.astype(np.uint8)

    # Convert (y, x) or (z, y, x) to NIfTI's (x, y[, z]) axes.
    nifti_data = np.flip(np.transpose(data), axis=(0, 1))
    affine = np.eye(4)
    for axis, spacing in enumerate(reversed(image.spacing)):
        affine[axis, axis] = spacing

    nib.save(nib.Nifti1Image(nifti_data, affine), file_path)
    return str(file_path)
