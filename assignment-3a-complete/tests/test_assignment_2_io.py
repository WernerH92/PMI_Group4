"""Regression tests for the restored Assignment 2A/2B I/O functions."""

import tempfile
import unittest
from pathlib import Path

import nibabel as nib
import numpy as np
from click.testing import CliRunner
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

from pmi_lib import DicomImage, Image, dicom_to_nifti, read_dicom, read_nifti, write_nifti
from pmi_lib.main import dicom_to_nifti_click


class Assignment2IOTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(prefix="pmi-a2-io-")
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.series_uid = generate_uid()
        self.pixels = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int16)

    def _write_slice(self, path: Path, z: float, series_uid: str | None = None) -> None:
        metadata = FileMetaDataset()
        metadata.TransferSyntaxUID = ExplicitVRLittleEndian
        metadata.MediaStorageSOPClassUID = CTImageStorage
        metadata.MediaStorageSOPInstanceUID = generate_uid()
        image = FileDataset(str(path), {}, file_meta=metadata, preamble=b"\0" * 128)
        image.SOPClassUID = metadata.MediaStorageSOPClassUID
        image.SOPInstanceUID = metadata.MediaStorageSOPInstanceUID
        image.SeriesInstanceUID = series_uid or self.series_uid
        image.StudyDescription = "Synthetic Assignment 2 test"
        image.Rows, image.Columns = self.pixels.shape
        image.SamplesPerPixel = 1
        image.PhotometricInterpretation = "MONOCHROME2"
        image.BitsAllocated = image.BitsStored = 16
        image.HighBit = 15
        image.PixelRepresentation = 1
        image.PixelSpacing = [0.75, 1.25]
        image.ImagePositionPatient = [0, 0, z]
        image.RescaleSlope = 2
        image.RescaleIntercept = -1024
        image.PixelData = (self.pixels + 10 * z).astype("<i2").tobytes()
        image.save_as(path, enforce_file_format=True)

    def test_nifti_round_trip_uses_matching_zyx_spacing(self) -> None:
        cases = (
            ((2, 3), (0.75, 1.25)),
            ((2, 3, 4), (3.0, 0.75, 1.25)),
        )
        for shape, spacing in cases:
            with self.subTest(shape=shape):
                data = np.arange(np.prod(shape), dtype=np.int16).reshape(shape)
                image = Image(data, spacing=spacing)
                output = self.root / f"{len(shape)}d.nii.gz"

                write_nifti(image, output)

                stored = nib.load(output)
                expected_data = np.flip(np.transpose(data), axis=(0, 1))
                np.testing.assert_array_equal(stored.get_fdata(), expected_data)
                self.assertEqual(stored.shape, tuple(reversed(shape)))
                np.testing.assert_allclose(
                    stored.header.get_zooms(), tuple(reversed(spacing))
                )

                restored = read_nifti(output)
                np.testing.assert_array_equal(np.asarray(restored), data)
                self.assertEqual(restored.spacing, spacing)

    def test_dicom_series_is_sorted_rescaled_and_uses_zyx(self) -> None:
        source = self.root / "series"
        source.mkdir()
        for name, z in (("late", 6), ("early", 0), ("middle", 3)):
            self._write_slice(source / f"{name}.dcm", z)

        image = read_dicom(source)

        self.assertIsInstance(image, DicomImage)
        self.assertEqual(np.shape(image), (3, 2, 3))
        self.assertEqual(image.spacing, (3.0, 0.75, 1.25))
        for index, z in enumerate((0, 3, 6)):
            np.testing.assert_array_equal(
                image[index], (self.pixels + 10 * z) * 2 - 1024
            )
        self.assertEqual(image.metadata["ImagePositionPatient"], [0, 0, 0])
        self.assertNotIn("PixelData", image.metadata)

        output = self.root / "converted.nii.gz"
        dicom_to_nifti(source, output)
        stored = nib.load(output)
        expected_data = np.flip(np.transpose(np.asarray(image)), axis=(0, 1))
        np.testing.assert_array_equal(stored.get_fdata(), expected_data)
        np.testing.assert_allclose(stored.affine, np.diag([1.25, 0.75, 3.0, 1.0]))
        restored = read_nifti(output)
        np.testing.assert_array_equal(np.asarray(restored), np.asarray(image))
        self.assertEqual(restored.spacing, image.spacing)

    def test_reader_rejects_mixed_series_and_missing_pixel_spacing(self) -> None:
        source = self.root / "mixed"
        source.mkdir()
        self._write_slice(source / "first.dcm", z=0)
        self._write_slice(source / "second.dcm", z=3, series_uid=generate_uid())
        with self.assertRaises(ValueError):
            read_dicom(source)

        missing_spacing = self.root / "missing_spacing.dcm"
        self._write_slice(missing_spacing, z=0)
        from pydicom import dcmread

        dataset = dcmread(missing_spacing)
        del dataset.PixelSpacing
        dataset.save_as(missing_spacing, enforce_file_format=True)
        with self.assertRaisesRegex(ValueError, "PixelSpacing"):
            read_dicom(missing_spacing)

    def test_cli_converts_a_file(self) -> None:
        source = self.root / "slice.dcm"
        output = self.root / "slice.nii.gz"
        self._write_slice(source, z=0)

        result = CliRunner().invoke(
            dicom_to_nifti_click,
            ["--file_path_dicom", str(source), "--file_path_nifti", str(output)],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
