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
from alinea.phenomenal.data_access.plant_1 import (
    plant_1_images,
    plant_1_mask_meanshift)

from alinea.phenomenal.display import (
    show_image)

from alinea.phenomenal.binarization import (
    mean_image,
    threshold_meanshift)

# ==============================================================================


def main():

    # Load images rotate side view series
    images = plant_1_images()

    # Select image camera side angle 120
    im = images['side'][120]

    # Show images selected
    show_image(im, name_windows="Original Image Selected")

    # Compute mean image of the camera side series
    mean_im = mean_image(images['side'].values())

    # Show mean image
    show_image(mean_im, name_windows="Mean Image")

    # Load meanshift mask
    mask = plant_1_mask_meanshift()

    # Show mask
    show_image(mask, name_windows="Mask")

    # Compute meanshift threshold
    bin_im = threshold_meanshift(im, mean_im, mask=mask)

    # Show binaries image
    show_image(bin_im, name_windows="Image Segmented")


if __name__ == "__main__":
    main()
