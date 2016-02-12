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
import cProfile
import time
import matplotlib.pyplot as plt

from alinea.phenomenal.plant_1 import (
    plant_1_calibration_camera_side_2_target,
    plant_1_images_binarize)

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d)

# ==============================================================================
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side_2_target()

# Select images
images_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    projection = calibration.get_projection(angle)
    images_projections.append((img, projection))


def profile(voxel_size):
    voxel_centers = reconstruction_3d(images_projections,
                                      voxel_size=voxel_size,
                                      verbose=False)


def time_processing(voxel_size, repetition=5):
    best = float('inf')
    mean = 0
    for i in range(repetition):
        start = time.time()
        profile(voxel_size)
        end = time.time() - start

        best = min(best, end)
        mean += end

    return best, mean / repetition

cProfile.run('profile(20)')

list_voxel_size = range(20, 10, -1)
list_best = list()
list_mean = list()
for voxel_size in list_voxel_size:
    best, mean = time_processing(voxel_size)
    print 'Voxel size : ', voxel_size, best, mean

    list_best.append(best)
    list_mean.append(mean)


plt.plot(list_voxel_size, list_best, 'bo')
plt.plot(list_voxel_size, list_mean, 'ro')
plt.show()