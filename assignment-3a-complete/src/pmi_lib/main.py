"""Click entry point for the Assignment 2A DICOM-to-NIfTI converter."""

import click

from .convert import dicom_to_nifti


@click.command()
@click.option(
    "--file_path_dicom",
    prompt="Input DICOM path",
    help="Path to the input DICOM file or directory.",
    required=True,
)
@click.option(
    "--file_path_nifti",
    prompt="Output NIFTI path",
    help="Path to the output NIFTI file.",
    required=True,
)
def dicom_to_nifti_click(file_path_dicom: str, file_path_nifti: str) -> None:
    """Convert a DICOM file or directory to NIfTI."""
    try:
        dicom_to_nifti(file_path_dicom, file_path_nifti)
    except FileNotFoundError:
        click.secho(f"Error: DICOM file not found - {file_path_dicom}", err=True, fg="red")
    except PermissionError:
        click.secho(f"Error: Permission denied to DICOM file - {file_path_dicom}", err=True, fg="red")
    except Exception as error:
        click.secho(f"Error: Unexpected error occurred: {error}", err=True, fg="red")
    else:
        click.secho(
            f"Read {file_path_dicom}, converted to {file_path_nifti}", fg="green"
        )


if __name__ == "__main__":
    dicom_to_nifti_click()
