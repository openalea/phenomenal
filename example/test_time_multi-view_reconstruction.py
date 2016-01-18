# -*- python -*-
#
#       test_time_multi-view_reconstruction.py : 
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
import time

import alinea.phenomenal.plant_1
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation

# ==============================================================================

radius = 10
verbose = True

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

images_selected = dict()
for angle in range(0, 360, 30):
    images_selected[angle] = images[angle]

# process_time = list()
# for i in range(10):
#     start_time = time.time()
#
#     points_3d, err = alinea.phenomenal.multi_view_reconstruction.\
#         reconstruction_3d(images_selected, projection, precision=radius,
#                           verbose=True)
#
#     process_time.append(time.time() - start_time)
#
# print process_time
# print 'Mean exec time (s) : ', sum(process_time) / len(process_time)

def foo():
    points_3d, err = alinea.phenomenal.multi_view_reconstruction.\
        reconstruction_3d(images_selected, projection, precision=radius,
                          verbose=True)


import cProfile
cProfile.run('foo()')


# radius = 10

# I - little with first split
# 1: 4.506
# 2: 5.10
# 3: 4.77

# II - Basic with dict optimization
# 1: 4.54
# 2: 4.75
# 3: 5.21

# III - Without dict optimization
# 1. 4.09
# 2. 4.42
# 3. 5.70
# 4. 4.55
