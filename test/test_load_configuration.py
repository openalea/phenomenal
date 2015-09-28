# -*- python -*-
#
#       test_load_configuration.py :
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
#       ========================================================================

#       ========================================================================
#       External Import

#       ========================================================================
#       Local Import 
import alinea.phenomenal.configuration


#       ========================================================================
#       Code


def test_load_configuration():
    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'factor_test_binarization.cfg')

    assert factor_side_binarization.cubicle_domain == (50, 1680, 275, 1746)
    assert factor_side_binarization.background is not None

    assert factor_side_binarization.roi_main.hsv_min == (30, 11, 0)
    assert factor_side_binarization.roi_main.hsv_max == (129, 254, 141)
    assert factor_side_binarization.roi_main.mask is not None

    assert factor_side_binarization.roi_stem.hsv_min == (30, 25, 0)
    assert factor_side_binarization.roi_stem.hsv_max == (150, 254, 165)
    assert factor_side_binarization.roi_stem.mask is not None

    assert factor_side_binarization.roi_pot.hsv_min == (14, 36, 0)
    assert factor_side_binarization.roi_pot.hsv_max == (88, 254, 88)
    assert factor_side_binarization.roi_pot.mask is not None

    assert factor_side_binarization.roi_orange_band.hsv_min == (19, 39, 0)
    assert factor_side_binarization.roi_orange_band.hsv_max == (104, 255, 132)
    assert factor_side_binarization.roi_orange_band.mask is not None

    assert factor_side_binarization.roi_panel.hsv_min is None
    assert factor_side_binarization.roi_panel.hsv_max is None
    assert factor_side_binarization.roi_panel.mask is not None

    assert factor_side_binarization.mean_shift_binarization_factor.\
        threshold == 0.5

    assert factor_side_binarization.mean_shift_binarization_factor.\
        dark_background is True


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_load_configuration()
