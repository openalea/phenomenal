# -*- python -*-
#
#       basic_usage.py : 
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
import cv2

#       ========================================================================
#       Local Import
import alinea.phenomenal.misc
import alinea.phenomenal.result_viewer
import alinea.phenomenal.configuration
import alinea.phenomenal.binarization
import alinea.phenomenal.data_transformation
import alinea.phenomenal.repair_processing
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction

#       ========================================================================
#       Code

data_directory = "..\\..\\local\\data set_0962_A310_ARCH2013-05-13\\"


images = alinea.phenomenal.misc.load_files(data_directory)

for pot_id in images:
    for date in images[pot_id]:

        files = images[pot_id][date]

        images[pot_id][date] = alinea.phenomenal.misc.load_images(
            files, cv2.IMREAD_UNCHANGED)

        print pot_id, date


alinea.phenomenal.result_viewer.show_images(
    [images['0962']['2013-06-22'][120], images['0962']['2013-06-22'][-1]])

factor_binarization = alinea.phenomenal.configuration.binarization_factor(
    'factor_image_basic.cfg')

img = images['0962']['2013-06-22']

images_binarize_mean_shift = alinea.phenomenal.binarization.binarization(
    img, factor_binarization, methods='mean_shift')

alinea.phenomenal.result_viewer.show_images(
    [images['0962']['2013-06-22'][120], images_binarize_mean_shift[120]])

repair_images = alinea.phenomenal.repair_processing.repair_processing(
    images_binarize_mean_shift)

alinea.phenomenal.result_viewer.show_images(
    [repair_images[120], images_binarize_mean_shift[120]])

calibration = alinea.phenomenal.calibration_model.Calibration.read_calibration(
    'tests/test_calibration_model')

images_selected = dict()
for angle in repair_images:
    if 0 <= angle <= 360:
        images_selected[angle] = repair_images[angle]


pixel_count = 0
for angle in images_selected:
    pixel_count += cv2.countNonZero(images_selected[angle])

import alinea.phenomenal.model

area = alinea.phenomenal.model.plant_area(pixel_count)

radius = 4
points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_selected, calibration, precision=radius)

alinea.phenomenal.result_viewer.show_points_3d(points_3d, scale_factor=2)

# points_3d = alinea.phenomenal.data_transformation.remove_internal_points_3d(
#     points_3d, radius)

alinea.phenomenal.result_viewer.show_points_3d(points_3d, scale_factor=2)


file_path = '../../local/test_test/file'
alinea.phenomenal.misc.write_xyz(points_3d, file_path)

points_3d = alinea.phenomenal.misc.read_xyz(file_path)

alinea.phenomenal.result_viewer.show_points_3d(points_3d, scale_factor=2)

matrix, index = alinea.phenomenal.data_transformation.points_3d_to_matrix(
    points_3d, radius)

points_3d = alinea.phenomenal.data_transformation.index_to_points_3d(
    index, 0.5)

import alinea.phenomenal.mesh

verts, faces = alinea.phenomenal.mesh.meshing(matrix)
normals = alinea.phenomenal.mesh.compute_normal(verts, faces)
centers = alinea.phenomenal.mesh.center_of_vertice(verts, faces)

centers
print verts
print faces

import numpy.linalg

print len(points_3d)
print len(centers)

normal_list = list()
for point_3d in points_3d:

    min_dist = float('inf')
    normal = None
    for i in range(len(centers)):

        distance = numpy.linalg.norm(point_3d - centers[i])

        if min_dist > distance:
            min_dist = distance
            normal = normals[i]

    print normal
    normal_list.append(normal)


import mayavi.mlab
mayavi.mlab.quiver3d(centers[:, 0], centers[:, 1], centers[:, 2],
                     normals[:, 0], normals[:, 1], normals[:, 2],
                     line_width=1.0,
                     scale_factor=1)

mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

mayavi.mlab.triangular_mesh([vert[0] for vert in verts],
                            [vert[1] for vert in verts],
                            [vert[2] for vert in verts],
                            faces)

# alinea.phenomenal.result_viewer.plot_points_3d(points_3d, scale_factor=1)

mayavi.mlab.show()
