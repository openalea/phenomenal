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
import numpy
# ==============================================================================

__all__ = ["show_image", "show_images"]

# ==============================================================================


def show_image(image, name_windows=''):
    matplotlib.pyplot.title(name_windows)

    if image.ndim == 2:
        img = image.astype(numpy.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        matplotlib.pyplot.imshow(img)
    else:
        matplotlib.pyplot.imshow(image)

    matplotlib.pyplot.show()


def show_images(images, name_windows='', names_axes=None):

    matplotlib.pyplot.title(name_windows)
    number_of_images = len(images)

    i = 1
    for image in images:
        ax = matplotlib.pyplot.subplot(1, number_of_images, i)

        if names_axes is None:
            ax.set_title('Image %d/%d' % (i, number_of_images))
        else:
            ax.set_title(names_axes[i])

        if image.ndim == 2:
            img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            ax.imshow(img)
        else:
            ax.imshow(image)

        i += 1

    matplotlib.pyplot.show()

