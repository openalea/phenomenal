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
    plant_1_images,
    plant_1_mask_meanshift,
    plant_1_mask_hsv)

from alinea.phenomenal.display import (
    show_image)

from alinea.phenomenal.binarization import (
    mean_image,
    threshold_meanshift,
    threshold_hsv)
# ==============================================================================


def run_threshold_meanshift(im, images):

    # Compute mean image of the camera side series
    mean_im = mean_image(images)

    # Show mean image
    show_image(mean_im, name_windows="Mean Image")

    # Load meanshift mask
    mask = plant_1_mask_meanshift()

    # Show mask
    show_image(mask, name_windows="Meanshift Mask")

    # Compute meanshift threshold
    bin_im = threshold_meanshift(im, mean_im, mask=mask)

    # Show binaries image
    show_image(bin_im, name_windows="Image Segmented with meanshift threshold")

    return bin_im


def run_threshold_hsv(im):

    # Convert BGR image to HSV image
    hsv_im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Declare HSV bounds who surround tint of plant to segment
    hsv_min = (30, 11, 0)
    hsv_max = (129, 254, 141)

    # Load HSV mask
    mask = plant_1_mask_hsv()

    # Show mask
    show_image(mask, name_windows="HSV Mask")

    # Compute hsv threshold
    bin_im = threshold_hsv(hsv_im, hsv_min, hsv_max, mask=mask)

    # Show binaries image
    show_image(bin_im, name_windows="Image Segmented with HSV threshold")

    return bin_im


def main():

    # Load images rotate side view series
    images = plant_1_images()

    # Select image camera side angle 120
    im = images['side'][120]

    # Show images selected
    show_image(im, name_windows="Original Image Selected")

    # Applied threshold meanshift algorithm
    meanshift_bin_im = run_threshold_meanshift(im, images['side'].values())

    # Applied threshold hsv algorithm
    hsv_bin_im = run_threshold_hsv(im)

    # Add two result together
    bin_im = cv2.add(hsv_bin_im, meanshift_bin_im)

    # Show binaries image
    show_image(bin_im, name_windows="Sum of binaries images")

    # Applied median blur
    median_blur_size = 3
    bin_im = cv2.medianBlur(bin_im, ksize=median_blur_size)

    # Show binaries image
    show_image(bin_im, name_windows="Image Segmented")

if __name__ == "__main__":
    main()
