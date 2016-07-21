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
    plant_1_calibration_camera_side)
# ==============================================================================


def test_projection_1():

    calibration = plant_1_calibration_camera_side()

    angle = 0
    pt_3d = (-472, -472, 200)
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1337.425449561377, 1070.8621710384346)

    angle = 0
    projection = calibration.get_projection(angle)
    pt_3d = (0.0, 0.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1021.5504552422917, 1261.7274393727464)

    pt_3d = (100.0, 100.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (963.19212737191492, 1261.5234983629146)

    angle = 90
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1125.9214666496891, 1262.0921778812051)

# ==============================================================================
# LOCAL TEST

if __name__ == "__main__":
    test_projection_1()
