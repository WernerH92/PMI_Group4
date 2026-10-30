from typing import Any

import numpy as np
import numpy.typing as npt


class Image:
    """Store a NumPy array together with one spacing value per array axis."""

    def __init__(
        self,
        data: np.ndarray,
        spacing: tuple[float | int, ...] | None = None,
    ) -> None:
        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a NumPy array")

        if spacing is None:
            # Images without physical metadata use one millimetre per axis.
            spacing = (1.0,) * data.ndim
        elif not isinstance(spacing, tuple):
            raise TypeError("spacing must be a tuple")
        elif not all(isinstance(value, (int, float)) for value in spacing):
            raise TypeError("spacing values must be integers or floats")

        if data.ndim != len(spacing):
            raise ValueError(
                f"image data with shape {data.shape} does not match "
                f"a spacing tuple of size {len(spacing)}"
            )

        self._data = data
        self.spacing = tuple(float(value) for value in spacing)

    def __str__(self) -> str:
        """Return a readable image description."""
        return (
            f"A {self._data.dtype} image with shape {self._data.shape} "
            f"and spacing {self.spacing} mm."
        )

    def __eq__(self, other: object) -> bool:
        """Return whether image data and spacing are both equal."""
        if not isinstance(other, Image):
            return NotImplemented
        return np.array_equal(self._data, other._data) and self.spacing == other.spacing

    def get_pixel_area(self) -> float:
        """Return the area of one pixel in square millimetres."""
        if len(self.spacing) < 2:
            raise ValueError("at least two dimensions are required for pixel area")
        # 2D data is (y, x); 3D data is (z, y, x).
        return float(self.spacing[-2] * self.spacing[-1])

    def get_voxel_volume(self) -> float:
        """Return the volume of one voxel in cubic millimetres."""
        if len(self.spacing) < 3:
            raise ValueError("at least three dimensions are required for voxel volume")
        return float(self.spacing[-3] * self.spacing[-2] * self.spacing[-1])

    def __len__(self) -> int:
        """Return the size of the first array axis."""
        return len(self._data)

    def __array__(
        self,
        dtype: npt.DTypeLike | None = None,
        copy: bool | None = None,
    ) -> np.ndarray:
        """Return the wrapped array so NumPy functions accept an Image."""
        return self._data.astype(dtype, copy=copy)

    def __getitem__(self, key: Any) -> Any:
        """Return an item or slice from the wrapped NumPy array."""
        return self._data[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item or slice in the wrapped NumPy array."""
        # NumPy performs the indexing, broadcasting, and dtype conversion.
        self._data[key] = value


class DicomImage(Image):
    """Store image data, spacing, and optional DICOM metadata."""

    def __init__(
        self,
        data: np.ndarray,
        spacing: tuple[float | int, ...] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary")

        super().__init__(data, spacing)
        self.metadata = metadata

    def __str__(self) -> str:
        """Return a readable DICOM image description."""
        return (
            f"A {self._data.dtype} image with shape {self._data.shape}, "
            f"spacing {self.spacing} mm, and metadata of type {type(self.metadata)}."
        )

    def __eq__(self, other: object) -> bool:
        """Return whether DICOM image data, spacing, and metadata are equal."""
        if not isinstance(other, DicomImage):
            return NotImplemented
        return (
            np.array_equal(self._data, other._data)
            and self.spacing == other.spacing
            and self.metadata == other.metadata
        )

