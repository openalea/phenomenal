# -*- python -*-
#
#       test_multi_view_reconstruction.py :
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
import collections

#       ========================================================================
#       Local Import
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model

#       ========================================================================
#       Code


def test_oct_split():

    point_3d = (0.0, 0.0, 0.0)
    radius = 8

    points_3d = alinea.phenomenal.multi_view_reconstruction.corners_point_3d(
        point_3d, radius / 2)

    assert len(points_3d) == 8

    assert points_3d[0] == (-4., -4., -4.)
    assert points_3d[1] == (4., -4., -4.)
    assert points_3d[2] == (-4., 4., -4.)
    assert points_3d[3] == (-4., -4., 4.)
    assert points_3d[4] == (4., 4., -4.)
    assert points_3d[5] == (4., -4., 4.)
    assert points_3d[6] == (-4., 4., 4.)
    assert points_3d[7] == (4., 4., 4.)


def test_split_cubes():

    point_3d = (0.0, 0.0, 0.0)
    radius = 8

    points_3d = collections.deque()
    points_3d.append(point_3d)

    l = alinea.phenomenal.multi_view_reconstruction.split_points_3d(
        points_3d, radius)

    assert len(l) == 8

    assert l[0] == (-4., -4., -4.)
    assert l[1] == (4., -4., -4.)
    assert l[2] == (-4., 4., -4.)
    assert l[3] == (-4., -4., 4.)
    assert l[4] == (4., 4., -4.)
    assert l[5] == (4., -4., 4.)
    assert l[6] == (-4., 4., 4.)
    assert l[7] == (4., 4., 4.)


def test_bbox_projection():
    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.data_load.\
        test_plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    point_3d = (0, 0, 0)
    radius = 4
    angle = 0

    res = alinea.phenomenal.multi_view_reconstruction.bbox_projection(
        point_3d, radius, projection, angle)

    assert res == (1016.657969220734,
                   1026.3381434879657,
                   1258.4181735951754,
                   1265.3138726030732)


def test_build_groups():

    # ==========================================================================
    # Load images binarize
    images = alinea.phenomenal.data_load.test_plant_1_images_binarize()

    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.data_load.\
        test_plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)
    # ==========================================================================

    angle_ref = 0
    radius = 10
    points_3d = collections.deque()
    points_3d.append((0.0, 0.0, 0.0))

    pts, groups = alinea.phenomenal.multi_view_reconstruction.build_groups(
        images, points_3d, angle_ref, projection, radius)

    pt1 = pts[0]

    pt = pt1[0]
    list_group = pt1[1]
    stat = pt1[2]

    print pt
    print stat
    print len(list_group)



    # print groups[0, 0]




#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_oct_split()
    test_split_cubes()
    test_bbox_projection()
    test_build_groups()
