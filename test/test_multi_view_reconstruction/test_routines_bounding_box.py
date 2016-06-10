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
from alinea.phenomenal.multi_view_reconstruction.routines import bounding_box

# ==============================================================================


def test_simply_working_1():

    voxel_centers = list()
    voxel_centers.append((0, 0, 0))
    voxel_centers.append((10, 10, 10))

    pt_min, pt_max = bounding_box(voxel_centers)

    assert pt_min == (0, 0, 0)
    assert pt_max == (10, 10, 10)

