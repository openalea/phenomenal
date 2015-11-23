# -*- python -*-
#
#       test_calibration_model_parameters.py : 
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
import alinea.phenomenal.calibration_model


def test_chessboard_model_parameters():
    obj = alinea.phenomenal.calibration_model.ChessboardModelParameters()

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

    obj.write('test')
    obj = alinea.phenomenal.calibration_model.ChessboardModelParameters.read(
        'test')

    parameters = obj.get_parameters()

    assert parameters[0] == 0
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4


def test_camera_model_parameters():
    obj = alinea.phenomenal.calibration_model.CameraModelParameters((0, 0))

    parameters = obj.get_parameters()
    assert parameters[0] == (0, 0)
    assert parameters[1] is None
    assert parameters[2] is None
    assert parameters[3] is None
    assert parameters[4] is None
    assert parameters[5] is None
    assert parameters[6] is None
    assert parameters[7] is None
    assert parameters[8] is None

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
    assert isinstance(parameters[8], float)

    parameters = obj.get_parameters()
    parameters[1] = 1
    parameters[2] = 2
    parameters[3] = 3
    parameters[4] = 4
    parameters[5] = 5
    parameters[6] = 6
    parameters[7] = 7
    parameters[8] = 8

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
    assert parameters[8] == 8

    obj.write('test')
    obj = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        'test')
    parameters = obj.get_parameters()

    assert parameters[0] == (0, 0)
    assert parameters[1] == 1
    assert parameters[2] == 2
    assert parameters[3] == 3
    assert parameters[4] == 4
    assert parameters[5] == 5
    assert parameters[6] == 6
    assert parameters[7] == 7
    assert parameters[8] == 8


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_chessboard_model_parameters()
    test_camera_model_parameters()