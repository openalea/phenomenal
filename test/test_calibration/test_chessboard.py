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
import numpy

from alinea.phenomenal.data_access.plant_1 import plant_1_images_chessboard
from alinea.phenomenal.calibration.chessboard import Chessboard
# ==============================================================================


def test_chessboard_1():
    chess = Chessboard(50, (8, 6))

    assert chess.square_size == 50
    assert chess.shape == (8, 6)
    assert chess.image_points == dict()


def test_chessboard_2():
    chess = Chessboard(50, (8, 6))

    result = chess.get_corners_local_3d()

    assert numpy.array_equal(result[8 * 0 + 0], [0., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 1], [50., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 2], [100., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 3], [150., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 4], [200., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 5], [250., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 6], [300., 0., 0.])
    assert numpy.array_equal(result[8 * 0 + 7], [350., 0., 0.])

    assert numpy.array_equal(result[8 * 5 + 0], [0., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 1], [50., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 2], [100., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 3], [150., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 4], [200., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 5], [250., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 6], [300., 250., 0.])
    assert numpy.array_equal(result[8 * 5 + 7], [350., 250., 0.])


def test_chessboard_3():
    chess = Chessboard(50, (8, 6))

    images = plant_1_images_chessboard()

    corners = chess.find_corners(images[42])

    ref = [[[901.7487793, 916.61584473]],
           [[943.39404297, 918.56256104]],
           [[984.82391357, 920.47631836]],
           [[1026.22973633, 922.36590576]],
           [[1067.45471191, 924.2479248]],
           [[1108.64367676, 926.16113281]],
           [[1149.7232666, 927.97131348]],
           [[1190.54919434, 929.85028076]],
           [[901.48706055, 956.45697021]],
           [[943.2366333, 958.35064697]],
           [[984.73040771, 960.19140625]],
           [[1026.25354004, 962.05499268]],
           [[1067.56323242, 963.90740967]],
           [[1108.83703613, 965.70666504]],
           [[1150.02807617, 967.56689453]],
           [[1190.96887207, 969.421875]],
           [[901.24841309, 996.38195801]],
           [[943.05218506, 998.23132324]],
           [[984.65789795, 1000.05755615]],
           [[1026.26660156, 1001.86462402]],
           [[1067.62536621, 1003.6864624]],
           [[1109.0057373, 1005.512146]],
           [[1150.26953125, 1007.33795166]],
           [[1191.36096191, 1009.13134766]],
           [[900.93981934, 1036.55749512]],
           [[942.81634521, 1038.36987305]],
           [[984.56585693, 1040.21179199]],
           [[1026.24536133, 1041.96362305]],
           [[1067.73913574, 1043.72363281]],
           [[1109.21435547, 1045.54223633]],
           [[1150.52648926, 1047.37353516]],
           [[1191.68164062, 1049.11962891]],
           [[900.65100098, 1077.00048828]],
           [[942.61108398, 1078.80981445]],
           [[984.47692871, 1080.58398438]],
           [[1026.23706055, 1082.36047363]],
           [[1067.81079102, 1084.10693359]],
           [[1109.3918457, 1085.83972168]],
           [[1150.75305176, 1087.59838867]],
           [[1192.00524902, 1089.36083984]],
           [[900.36218262, 1117.58496094]],
           [[942.43157959, 1119.37158203]],
           [[984.37243652, 1121.09423828]],
           [[1026.22521973, 1122.81933594]],
           [[1067.87414551, 1124.55603027]],
           [[1109.58569336, 1126.31738281]],
           [[1151.09484863, 1127.9473877]],
           [[1192.33251953, 1129.67236328]]]

    res = numpy.array(corners).astype(float)
    ref = numpy.array(ref).astype(float)
    res = numpy.around(res, decimals=1)
    ref = numpy.around(ref, decimals=1)
    assert numpy.array_equiv(res, ref)

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()

