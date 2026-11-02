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

class SphericalMeasurement:
    def __init__(self,
                radius: float,
                functions: dict[str, Callable]):   
        if not isinstance(radius, (int,float)) or radius <= 0:
            raise ValueError('radius must be a positive integer or float.')
        elif type(functions) != dict:
            raise ValueError('function imput must be a dictionary.')

        else:
            self.radius = radius
            self.functions = functions
        
    def __call__(self,
                image: Image,
                x: int, y: int, z: int) -> dict[str, Any]:
        if not isinstance(image, Image):
            raise ValueError('input image must be an Image object.')
        if not all(isinstance(i, int) for i in (x,y,z)):
            raise ValueError('input coordinates must be integer values.') 
        
        self.image = image
        self.voxels = [x, y, z]

        data = np.array(image._data)
        sz, sy, sx = image.spacing

        if data.ndim != 3:
            raise ValueError('SphericalMeasurement requires a 3D image.')

        # Calculate sphere radius in voxels
        rx = int(np.ceil(self.radius / sx))
        ry = int(np.ceil(self.radius / sy))
        rz = int(np.ceil(self.radius / sz))

        # Calculate crop boundaries
        x0 = max(0, x - rx)
        x1 = min(data.shape[2], x + rx + 1)
        y0 = max(0, y - ry)
        y1 = min(data.shape[1], y + ry + 1)
        z0 = max(0, z - rz)
        z1 = min(data.shape[0], z + rz + 1)

        # Crop image around the sphere
        cropped = data[z0:z1, y0:y1, x0:x1]

        # Create coordinate grids
        zz, yy, xx = np.indices(cropped.shape)

        # Create spherical mask
        mask = (
            ((xx + x0 - x) * sx) ** 2 +
            ((yy + y0 - y) * sy) ** 2 +
            ((zz + z0 - z) * sz) ** 2
            <= self.radius ** 2
        )

        # Extract voxel values inside the sphere
        flattened_pixel_data = cropped[mask]

        # Create a copy of the cropped image
        selection = cropped.astype(float, copy=True)

        # Calculate reference intensity
        reference_intensity = np.percentile(cropped, 5)

        # Darken the area outside the sphere
        darkening = 0.10
        selection[~mask] = (
            reference_intensity +
            darkening * (cropped[~mask] - reference_intensity)
        )
        results = {}
        for key, value in self.functions.items(): #for every statistic in binary:
            f = value   #f is one function (value)
            results[key] = f(flattened_pixel_data)

        results['image'] = selection
        return results