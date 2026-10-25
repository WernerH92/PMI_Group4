import unittest

import numpy as np

from pmi_lib import Image, bilateral_filter, bilateral_filter_py


class Assignment3ATests(unittest.TestCase):
    def test_image_setitem_updates_the_wrapped_array(self) -> None:
        image = Image(np.zeros((2, 3)), spacing=(1.0, 2.0))

        image[1, 2] = 7.5

        self.assertEqual(image[1, 2], 7.5)
        self.assertEqual(image._data[1, 2], 7.5)

    def test_python_and_c_filters_agree_for_2d_images(self) -> None:
        random = np.random.default_rng(42)
        cases = [
            ((1, 100), (1.0, 2.0)),
            ((100, 1), (2.0, 1.0)),
            ((8, 9), (1.25, 0.75)),
        ]

        for shape, spacing in cases:
            with self.subTest(shape=shape, spacing=spacing):
                data = random.normal(size=shape)
                data_copy = data.copy()
                image = Image(data, spacing=spacing)

                result_py = bilateral_filter_py(image, sigma_s=2.5, sigma_r=0.8)
                result_c = bilateral_filter(image, sigma_s=2.5, sigma_r=0.8)

                np.testing.assert_array_equal(image._data, data_copy)
                self.assertEqual(result_py.spacing, spacing)
                self.assertEqual(result_c.spacing, spacing)
                np.testing.assert_allclose(
                    np.asarray(result_py),
                    np.asarray(result_c),
                    rtol=1e-12,
                    atol=1e-12,
                )

    def test_bilateral_filter_preserves_a_constant_image(self) -> None:
        image = Image(np.full((7, 6), 3.25), spacing=(0.8, 1.2))

        result_py = bilateral_filter_py(image, sigma_s=2.0, sigma_r=1.0)
        result_c = bilateral_filter(image, sigma_s=2.0, sigma_r=1.0)

        np.testing.assert_allclose(np.asarray(result_py), image._data)
        np.testing.assert_allclose(np.asarray(result_c), image._data)

    def test_bilateral_filters_reject_non_2d_images(self) -> None:
        images = [
            Image(np.ones(5), spacing=(1.0,)),
            Image(np.ones((2, 3, 4)), spacing=(1.0, 1.0, 1.0)),
        ]

        for image in images:
            with self.subTest(shape=image._data.shape):
                with self.assertRaises(ValueError):
                    bilateral_filter_py(image, sigma_s=1.0, sigma_r=1.0)
                with self.assertRaises(ValueError):
                    bilateral_filter(image, sigma_s=1.0, sigma_r=1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
