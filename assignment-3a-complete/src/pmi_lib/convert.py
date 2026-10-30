"""DICOM-to-NIfTI conversion helper used by the public CLI."""

from os import PathLike

from .dicom import read_dicom
from .nifti import write_nifti


def dicom_to_nifti(
    file_path_dicom: str | PathLike[str],
    file_path_nifti: str | PathLike[str],
) -> None:
    """Convert one DICOM image or series into a NIfTI file."""
    write_nifti(read_dicom(file_path_dicom), file_path_nifti)
