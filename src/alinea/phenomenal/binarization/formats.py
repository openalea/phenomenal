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
import cv2
# ==============================================================================

__all__ = ["read_image", "write_image"]

# ==============================================================================


def read_image(file_name, cv2_flag=cv2.IMREAD_UNCHANGED):
    return cv2.imread(file_name, flags=cv2_flag)


def write_image(image, file_name):
    cv2.imwrite(file_name, image)
