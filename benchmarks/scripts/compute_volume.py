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

from alinea.phenomenal.plant_1 import (
    plant_1_calibration_camera_side_2_target,
    plant_1_images_binarize)

import alinea.phenomenal.calibration_model
from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d,
    volume)

import alinea.phenomenal.viewer
import alinea.phenomenal.misc
# ==============================================================================


def dump(list_volume, list_radius):
    save_volumes = dict()
    save_volumes['list_volume'] = list_volume
    save_volumes['list_radius'] = list(list_radius)

    with open('volumes.json', 'w') as output_file:
        json.dump(save_volumes, output_file)


def load():
    with open('volumes.json', 'r') as input_file:
        save_volumes = json.load(input_file)

    list_volume = save_volumes['list_volume']
    list_radius = save_volumes['list_radius']

    return list_volume, list_radius


# ==============================================================================
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side_2_target()

images_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    projection = calibration.get_projection(angle)
    images_projections.append((img, projection))

# ==============================================================================

save_points = dict()
list_voxel_size = numpy.arange(20, 9, -1)
list_volume = list()
list_sum_error_precision = list()

for voxel_size in list_voxel_size:
    voxel_centers = reconstruction_3d(
        images_projections, voxel_size=voxel_size, verbose=True)

    save_points[voxel_size] = voxel_centers

    v = volume(voxel_centers, voxel_size)
    list_volume.append(v)

    print 'Voxel_size', voxel_size,
    print '- Volume :', v

# ==============================================================================

dump(list_volume, list_voxel_size)
list_volume, list_voxel_size = load()

plt.plot(list_voxel_size, list_volume, 'bo')
plt.show()

# ==============================================================================

mayavi.mlab.figure('3d')
mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

alinea.phenomenal.viewer.plot_points_3d(save_points[20])
alinea.phenomenal.viewer.plot_points_3d(save_points[10])
mayavi.mlab.show()

