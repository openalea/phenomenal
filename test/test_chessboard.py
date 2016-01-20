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

from alinea.phenomenal.chessboard import Chessboard
# ==============================================================================


def test_chessboard_1():
    chess = Chessboard(50, (8, 6))

    assert chess.square_size == 50
    assert chess.shape == (8, 6)
    assert chess.corners_points == dict()


def test_chessboard_2():
    chess = Chessboard(50, (8, 6))

    result = chess.local_corners_position_3d()
    print numpy.array(result)

    

if __name__ == "__main__":
    test_chessboard_1()
    test_chessboard_2()
