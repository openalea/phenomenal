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
from matplotlib import pyplot as plt
# ==============================================================================

__all__ = ["show_image", "show_images"]

# ==============================================================================


def _imshow(ax, image):
    """Show a grayscale (2-D, in gray levels) or RGB(A) image on ax, as uint8"""
    image = numpy.asarray(image)
    if image.dtype == bool:
        image = image.astype(numpy.uint8) * 255
    image = numpy.array(numpy.round(image), dtype=numpy.uint8)
    if image.ndim == 2:
        ax.imshow(image, cmap="gray", vmin=0, vmax=255)
    else:
        ax.imshow(image)


def show_image(image, title=""):
    plt.title(title)
    plt.axis('off')
    _imshow(plt.gca(), image)
    plt.show()


def show_images(images, title=None):

    if isinstance(title, str):
        plt.suptitle(title)
        title = None

    nb_col = min(len(images), 4)
    nb_row = int(math.ceil(len(images) / float(nb_col)))

    for i, image in enumerate(images, 1):
        ax = plt.subplot(nb_row, nb_col, i)
        ax.axis("off")

        if title is not None:
            ax.set_title(title[i - 1])

        _imshow(ax, image)

    plt.show()
