"""DICOM reading for images stored as ``(y, x)`` or ``(z, y, x)``."""

import os

import numpy as np
from pydicom import dcmread

from .image import DicomImage


def _get_z_position(dicom_dataset) -> float:
    """Return the z-coordinate used to sort a DICOM series."""
    return float(dicom_dataset.ImagePositionPatient[2])


def _get_spacing(dicom_slices: list) -> tuple[float, ...]:
    """Return spacing in the same axis order as the returned array."""
    if not hasattr(dicom_slices[0], "PixelSpacing"):
        raise ValueError("DICOM image must provide PixelSpacing in millimetres")

    spacing_y, spacing_x = (float(value) for value in dicom_slices[0].PixelSpacing)
    if len(dicom_slices) == 1:
        return spacing_y, spacing_x

    first_position = np.asarray(dicom_slices[0].ImagePositionPatient, dtype=float)
    last_position = np.asarray(dicom_slices[-1].ImagePositionPatient, dtype=float)
    spacing_z = np.linalg.norm(last_position - first_position) / (len(dicom_slices) - 1)
    return float(spacing_z), spacing_y, spacing_x


def _metadata(dicom_dataset) -> dict:
    """Copy named DICOM attributes without the large raw PixelData element."""
    return {
        item.keyword: item.value
        for item in dicom_dataset
        if item.keyword and item.keyword != "PixelData"
    }


def read_dicom(file_path: str | os.PathLike[str]) -> DicomImage:
    """Read one DICOM file or a folder containing one DICOM series.

    A series is sorted by patient z-position and stacked into a ``(z, y, x)``
    array. Its spacing is returned as ``(spacing_z, spacing_y, spacing_x)``.
    """
    if os.path.isfile(file_path):
        dicom_slices = [dcmread(file_path)]
    elif os.path.isdir(file_path):
        dicom_files = [
            os.path.join(file_path, name)
            for name in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, name))
        ]
        if not dicom_files:
            raise FileNotFoundError(f"No files found in directory: {file_path}")
        dicom_slices = [dcmread(path) for path in dicom_files]
        dicom_slices.sort(key=_get_z_position)
    else:
        raise FileNotFoundError(f"Could not find file or directory: {file_path}")

    series_uids = [dataset.SeriesInstanceUID for dataset in dicom_slices]
    if not all(uid == series_uids[0] for uid in series_uids):
        raise ValueError(f"Directory {file_path} contains multiple Series Instance UIDs")

    pixel_slices = []
    for dataset in dicom_slices:
        slope = getattr(dataset, "RescaleSlope", 1.0)
        intercept = getattr(dataset, "RescaleIntercept", 0.0)
        pixel_slices.append(dataset.pixel_array * slope + intercept)

    data = pixel_slices[0] if len(pixel_slices) == 1 else np.stack(pixel_slices, axis=0)
    return DicomImage(data, _get_spacing(dicom_slices), _metadata(dicom_slices[0]))
