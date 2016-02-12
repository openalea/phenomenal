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

from alinea.phenomenal.plant_1 import (
    plant_1_calibration_camera_side_2_target)
# ==============================================================================


def test_projection_1():

    calibration = plant_1_calibration_camera_side_2_target()

    angle = 0
    pt_3d = (-472, -472, 200)
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1465.5468883568233, 1074.736078031063)

    angle = 0
    projection = calibration.get_projection(angle)
    pt_3d = (0.0, 0.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1021.5053162011903, 1260.9652045590892)

    pt_3d = (100.0, 100.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (937.24706174348887, 1260.6718179928703)

    angle = 90
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1105.7594000551171, 1261.2585766032989)

# ==============================================================================
# LOCAL TEST

if __name__ == "__main__":
    test_projection_1()
