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
import json
import mayavi.mlab
import matplotlib.pyplot as plt
import numpy
import collections

import alinea.phenomenal.plant_1
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
# ==============================================================================


def save(list_volume, list_radius, list_sum_error_precision):
    save_volumes = dict()
    save_volumes['list_volume'] = list_volume
    save_volumes['list_radius'] = list(list_radius)
    save_volumes['list_sum_error_precision'] = list_sum_error_precision

    with open('volumes.json', 'w') as output_file:
        json.dump(save_volumes, output_file)


def load():
    with open('volumes.json', 'r') as input_file:
        save_volumes = json.load(input_file)

    list_volume = save_volumes['list_volume']
    list_radius = save_volumes['list_radius']
    list_sum_error_precision = save_volumes['list_sum_error_precision']

    return list_volume, list_radius, list_sum_error_precision


def compute_sum(points_3d, radius, images_selected, projection):
    sum_error_precision = 0
    sum_volumes_images = 0
    for angle in images_selected:
        # Build image projection of points_3d cloud
        img = alinea.phenomenal.multi_view_reconstruction.\
            project_points_on_image(points_3d,
                                    radius,
                                    images_selected[angle].shape,
                                    projection,
                                    angle)

        img = img.astype(numpy.uint8)

        sum_volumes_images += numpy.count_nonzero(img)

        image_diff = numpy.subtract(img, images_selected[angle])
        image_diff[image_diff == -255] = 0
        image_diff = image_diff.astype(numpy.uint8)

        error_precision = numpy.count_nonzero(image_diff)
        sum_error_precision += error_precision

    return sum_error_precision, sum_volumes_images

# ==============================================================================

# Load images binarize
images = alinea.phenomenal.plant_1.plant_1_images_binarize()

# Load camera model parameters
params_camera_path, _ = alinea.phenomenal.plant_1.\
    plant_1_calibration_params_path()

cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
    params_camera_path)

# Create model projection object
projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

# Select images
images_selected = dict()
for angle in range(0, 360, 30):
    images_selected[angle] = images[angle]

# ==============================================================================

save_points = dict()
list_radius = numpy.arange(10, 3, -1)
list_volume = list()
list_sum_error_precision = list()

for radius in list_radius:
    # Multi-view reconstruction
    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images_selected, projection, radius, verbose=True)

    save_points[radius] = points_3d

    volume = len(points_3d) * (radius**3)
    list_volume.append(volume)

    sum_error_precision, sum_volumes_images = compute_sum(
        points_3d, radius, images_selected, projection)

    list_sum_error_precision.append(sum_error_precision)

    print 'Radius', radius,
    print '- Volume :', volume,
    print '- Sum error precision :', sum_error_precision,
    print '- Sum volumes images :', sum_volumes_images

# ==============================================================================

save(list_volume, list_radius, list_sum_error_precision)
list_volume, list_radius, list_sum_error_precision = load()

plt.plot(list_radius, list_sum_error_precision, 'ro')
plt.plot(list_radius, list_volume, 'bo')
plt.show()

# ==============================================================================

mayavi.mlab.figure('3d')
mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

alinea.phenomenal.viewer.plot_points_3d(save_points[8])
alinea.phenomenal.viewer.plot_points_3d(save_points[4])
mayavi.mlab.show()

