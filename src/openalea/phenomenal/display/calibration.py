# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
"""
Modules to display calibration result
"""

# ==============================================================================




import cv2

from openalea.phenomenal.optional_deps import require_dependency
# ==============================================================================

__all__ = [
    "show_image_with_chessboard_corners",
    "show_chessboard_3d_projection_on_image",
]

# ==============================================================================


def show_image_with_chessboard_corners(image, corners, name_windows=""):
    plt = require_dependency('matplotlib.pyplot', 'viz')
    img = image.copy()

    corners = corners.astype(int)
    img[corners[:, 0, 1], corners[:, 0, 0]] = [0, 0, 255]

    plt.title(name_windows)
    plt.imshow(img)
    plt.show()


def show_chessboard_3d_projection_on_image(
    image, points_2d_1, points_2d_2, figure_name=""
):
    plt = require_dependency('matplotlib.pyplot', 'viz')
    img = image.copy()

    points_2d_1 = points_2d_1.astype(int)
    img[points_2d_1[:, 0, 1], points_2d_1[:, 0, 0]] = [0, 0, 0]

    for x, y in points_2d_2:
        img[int(y), int(x)] = [255, 0, 0]

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    plt.figure(figure_name)
    plt.imshow(img)
    plt.show()
