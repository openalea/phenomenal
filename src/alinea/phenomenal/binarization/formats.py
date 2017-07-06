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
Formats module to read/write image
"""
# ==============================================================================
import os
import cv2
# ==============================================================================

__all__ = ["read_image", "write_image"]

# ==============================================================================


def read_image(filename, flags=cv2.IMREAD_UNCHANGED):
    return cv2.imread(filename, flags=flags)


def write_image(filename, image):

    if (os.path.dirname(filename) and not os.path.exists(
            os.path.dirname(filename))):
        os.makedirs(os.path.dirname(filename))

    cv2.imwrite(filename, image)
