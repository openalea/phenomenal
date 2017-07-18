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

from alinea.phenomenal.multi_view_reconstruction.multi_view_reconstruction\
    import (get_bounding_box_voxel_projected)

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_calibration_camera_side)
# ==============================================================================


def test_bbox_projected_1():

    voxel_center = numpy.array([[0, 0, 0]])
    voxel_size = 20

    projection = lambda pt: numpy.column_stack((pt[:, 0], pt[:, 1]))

    res = get_bounding_box_voxel_projected(voxel_center, voxel_size, projection)
    ref = numpy.array([[-10, -10, 10, 10]])

    assert numpy.allclose(ref, res)


def test_bbox_projected_2():

    angle = 0
    calibration = plant_1_calibration_camera_side()
    projection = calibration.get_projection(angle)

    voxels_position = numpy.array([[0, 0, 0],
                                   [0, 0, 0],
                                   [0, 0, 0]])
    voxels_size = 8

    res = get_bounding_box_voxel_projected(voxels_position,
                                           voxels_size,
                                           projection)

    ref = numpy.array([[1017.309, 1258.280, 1025.788, 1265.171],
                       [1017.309, 1258.280, 1025.788, 1265.171],
                       [1017.309, 1258.280, 1025.788, 1265.171]])

    assert numpy.allclose(ref, res)

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
