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

from alinea.phenomenal.binarization.formats import read_image

# ==============================================================================


def test_simply_working_1():

    file_name = os.path.dirname(__file__) + "/data/150.png"
    im = read_image(file_name)

    assert im.shape == (495, 415, 3)

if __name__ == "__main__":
    test_simply_working_1()
