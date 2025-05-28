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
Module to display image and binarization result
"""

# ==============================================================================
from __future__ import division, print_function, absolute_import

import math
from PIL import Image
import numpy

from openalea.phenomenal.optional_deps import require_dependency
# ==============================================================================

__all__ = ["show_image", "show_images"]

# ==============================================================================


def show_image(image, name_windows=""):
    plt = require_dependency('matplotlib.pyplot', 'plot')
    plt.title(name_windows)

    if image.ndim == 2:
        img = image.astype(numpy.uint8)
        img = img[:, :, ::-1].copy()
        plt.imshow(img)
    else:
        plt.imshow(image)

    plt.show()


def show_images(images, name_windows=""):
    plt = require_dependency('matplotlib.pyplot', 'plot')
    plt.title(name_windows)
    nb_col = min(len(images), 4)
    nb_row = int(math.ceil(len(images) / float(nb_col)))

    for i, image in enumerate(images, 1):
        image = numpy.array(numpy.round(image), dtype=numpy.uint8)
        ax = plt.subplot(nb_row, nb_col, i)
        ax.axis("off")
        if image.ndim == 2:
            img = Image.fromarray(image).convert("RGB")
            ax.imshow(img)
        else:
            ax.imshow(image)

    plt.show()
