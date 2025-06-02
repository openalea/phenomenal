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
import math
import numpy
from PIL import Image
from openalea.phenomenal.optional_deps import require_dependency
# ==============================================================================

__all__ = ["show_image", "show_images"]

# ==============================================================================


def show_image(image, name_windows=""):
    plt = require_dependency('matplotlib.pyplot', 'viz')
    plt.title(name_windows)
    plt.axis('off')
    plt.imshow(Image.fromarray(image).convert("RGB"))
    plt.show()


def show_images(images, name_windows=""):
    plt = require_dependency('matplotlib.pyplot', 'viz')
    plt.title(name_windows)
    plt.axis('off')
    nb_col = min(len(images), 4)
    nb_row = int(math.ceil(len(images) / float(nb_col)))

    for i, image in enumerate(images, 1):
        image = numpy.array(numpy.round(image), dtype=numpy.uint8)
        ax = plt.subplot(nb_row, nb_col, i)
        ax.axis("off")
        ax.imshow(Image.fromarray(image).convert("RGB"))
    plt.show()
