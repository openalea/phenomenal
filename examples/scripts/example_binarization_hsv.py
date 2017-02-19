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
import cv2

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_images)

from alinea.phenomenal.display import (
    show_image)

from alinea.phenomenal.binarization import (
    threshold_hsv)

# ==============================================================================


def main():

    # Load images rotate side view series
    images = plant_1_images()

    # Select image camera top angle 0
    im = images['top'][0]

    # Show images selected
    show_image(im, name_windows="Original Image Selected")

    # Convert BGR image to HSV image
    hsv_im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Declare HSV bounds who surround tint of plant to segment for top camera
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)

    # Compute hsv threshold
    bin_im = threshold_hsv(hsv_im, hsv_min, hsv_max, mask=None)

    # Show binaries image
    show_image(bin_im, name_windows="Image Segmented")


if __name__ == "__main__":
    main()
