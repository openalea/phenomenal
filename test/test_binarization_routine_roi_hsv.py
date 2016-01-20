# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import numpy

from alinea.phenomenal.plant_1 import (plant_1_images,
                                       plant_1_mask_hsv_roi_main,
                                       plant_1_mask_hsv_roi_band,
                                       plant_1_mask_hsv_roi_pot,
                                       plant_1_background_hsv)

from alinea.phenomenal.binarization_routine import roi_hsv
# ==============================================================================


# def test_side_binarization_hsv_1():
#
#     factor = binarization_factor('factor_image_basic.cfg')
#     image = numpy.zeros((2454, 2056, 3), dtype=numpy.uint8)
#
#     binarize_image = side_binarization_hsv(image, factor)
#
#     assert (binarize_image == 0).all()
#     assert binarize_image.ndim == 2
#     assert binarize_image.shape == (2454, 2056)


def test_no_regression_1():

    cubicle_domain = (0, 2190, 275, 1746)
    cubicle_background = plant_1_background_hsv()
    main_hsv_min = (30, 11, 0)
    main_hsv_max = (129, 254, 141)
    main_mask = plant_1_mask_hsv_roi_main()
    orange_band_mask = plant_1_mask_hsv_roi_band()
    pot_hsv_min = (14, 36, 0)
    pot_hsv_max = (88, 254, 88)
    pot_mask = plant_1_mask_hsv_roi_pot()

    images = plant_1_images()
    images.pop(-1)

    refs = [(0, 121726),
            (30, 104465),
            (60, 141807),
            (90, 126528),
            (120, 114964),
            (150, 118759),
            (180, 118949),
            (210, 83357),
            (240, 139211),
            (270, 120737),
            (300, 108052),
            (330, 113243)]

    for angle, ref in refs:
        image_0_binarize = roi_hsv(
            images[angle],
            cubicle_domain,
            cubicle_background,
            main_hsv_min,
            main_hsv_max,
            main_mask,
            orange_band_mask,
            pot_hsv_min,
            pot_hsv_max,
            pot_mask)

        assert numpy.count_nonzero(image_0_binarize) == ref


# ==============================================================================

if __name__ == "__main__":
    # test_side_binarization_hsv_1()

    test_no_regression_1()
