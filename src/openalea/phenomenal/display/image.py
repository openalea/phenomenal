# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
"""
Module to display image and binarization result
"""
# ==============================================================================
import matplotlib.pyplot
import cv2
import math
import numpy
# ==============================================================================

__all__ = ["show_image", "show_images"]

# ==============================================================================


def show_image(image, name_windows=''):
    matplotlib.pyplot.title(name_windows)

    if image.ndim == 2:
        img = image.astype(numpy.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        matplotlib.pyplot.imshow(img)
    else:
        matplotlib.pyplot.imshow(image)

    matplotlib.pyplot.show()


def show_images(images, name_windows=''):

    matplotlib.pyplot.title(name_windows)
    nb_col = 4
    nb_row = int(math.ceil(len(images) / float(nb_col)))

    for i, image in enumerate(images, 1):
        ax = matplotlib.pyplot.subplot(nb_row, nb_col, i)
        ax.axis('off')
        if image.ndim == 2:
            img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            ax.imshow(img)
        else:
            ax.imshow(image)

    matplotlib.pyplot.show()
    matplotlib.pyplot.tight_layout(h_pad=0.050, w_pad=0.001)

