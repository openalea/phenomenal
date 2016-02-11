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
import os

from alinea.phenomenal.calibration_model import (ChessboardModelParameters,
                                                 CameraModelParameters)
# =============================================================================


def test_chessboard_model_parameters():
    obj = ChessboardModelParameters()

    parameters = obj.get_parameters()
    assert parameters[0] is None
    assert parameters[1] is None
    assert parameters[2] is None
    assert parameters[3] is None
    assert parameters[4] is None

    obj.random_initialization()
    parameters = obj.get_parameters()

    assert isinstance(parameters[0], float)
    assert isinstance(parameters[1], float)
    assert isinstance(parameters[2], float)
    assert isinstance(parameters[3], float)
    assert isinstance(parameters[4], float)

    parameters = obj.get_parameters()
    parameters[0] = 0
    parameters[1] = 1
    parameters[2] = 2
    parameters[3] = 3
    parameters[4] = 4
    obj.set_parameters(*parameters)
    parameters = obj.get_parameters()

    assert parameters[0] == 0
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4

    obj.write('test_chessboard_model_parameters')
    obj = ChessboardModelParameters.read('test_chessboard_model_parameters')

    parameters = obj.get_parameters()

    assert parameters[0] == 0
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4

    os.remove('test_chessboard_model_parameters.json')

def test_camera_model_parameters():
    obj = CameraModelParameters((0, 0))

    parameters = obj.get_parameters()
    assert parameters[0] == (0, 0)
    assert parameters[1] is None
    assert parameters[2] is None
    assert parameters[3] is None
    assert parameters[4] is None
    assert parameters[5] is None
    assert parameters[6] is None
    assert parameters[7] is None

    obj.random_initialization()
    parameters = obj.get_parameters()

    assert isinstance(parameters[0], tuple)
    assert isinstance(parameters[1], float)
    assert isinstance(parameters[2], float)
    assert isinstance(parameters[3], float)
    assert isinstance(parameters[4], float)
    assert isinstance(parameters[5], float)
    assert isinstance(parameters[6], float)
    assert isinstance(parameters[7], float)

    parameters = obj.get_parameters()
    parameters[1] = 1
    parameters[2] = 2
    parameters[3] = 3
    parameters[4] = 4
    parameters[5] = 5
    parameters[6] = 6
    parameters[7] = 7

    obj.set_parameters(*parameters[1:])
    parameters = obj.get_parameters()

    assert parameters[0] == (0, 0)
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4
    assert parameters[5] == 5
    assert parameters[6] == 6
    assert parameters[7] == 7

    obj.write('test_camera_model_parameters')
    obj = CameraModelParameters.read('test_camera_model_parameters')
    parameters = obj.get_parameters()

    assert parameters[0] == (0, 0)
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4
    assert parameters[5] == 5
    assert parameters[6] == 6
    assert parameters[7] == 7

    os.remove('test_camera_model_parameters.json')

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_chessboard_model_parameters()
    test_camera_model_parameters()