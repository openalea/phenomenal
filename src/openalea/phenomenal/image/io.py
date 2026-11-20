# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
Formats module to read/write image
"""

# ==============================================================================

import os

import cv2
import numpy

# ==============================================================================

__all__ = ["read_image", "write_image"]

# PIL-like flags (modes) accepted by read_image
_READ_FLAGS = {
    None: cv2.IMREAD_UNCHANGED,
    "RGB": cv2.IMREAD_COLOR,
    "L": cv2.IMREAD_GRAYSCALE,
}


def read_image(filename, flag=None):
    """
    Read an image from a file, with OpenCV.

    Colour images are returned in RGB order (OpenCV reads them in BGR order),
    the convention of the phenomenal image routines.

    Parameters
    ----------
    filename : str or path-like
        file name of the image
    flag : {None, 'RGB', 'L'}, optional
        None (default) reads the image as it is (grayscale, RGB or RGBA),
        'RGB' converts it to a colour image, and 'L' to a grayscale image.

    Returns
    -------
    img : numpy.ndarray
        RGB (3-D), RGBA (3-D) or grayscale (2-D) image
    """
    if flag not in _READ_FLAGS:
        raise ValueError(f"flag must be one of {list(_READ_FLAGS)}, not {flag!r}")
    # imdecode instead of imread: cv2.imread does not read non-ASCII paths on Windows
    data = numpy.fromfile(str(filename), dtype=numpy.uint8)
    img = cv2.imdecode(data, _READ_FLAGS[flag])
    if img is None:
        raise IOError(f"Cannot read image {filename}")

    if img.ndim == 3:
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

    return img


def write_image(filename, image):
    """
    Write an image in a file, with OpenCV.

    Parameters
    ----------
    filename : str or path-like
        output filename where write the image. The extension gives the format.
    image : numpy.ndarray
        grayscale (2-D), RGB or RGBA (3-D) image, as returned by `read_image`.
        It is converted to uint8.

    Returns
    -------
    None
    """
    filename = str(filename)
    if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    image = numpy.asarray(image).astype(numpy.uint8)
    if image.ndim == 3:
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    # imencode instead of imwrite: cv2.imwrite does not write non-ASCII paths on Windows
    ok, data = cv2.imencode(os.path.splitext(filename)[1], image)
    if not ok:
        raise IOError(f"Cannot write image {filename}")
    data.tofile(filename)
