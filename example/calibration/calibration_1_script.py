# -*- python -*-
#
#       calibration_1_script.py :
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
import glob
import cv2

#       ========================================================================
#       Local Import
import alinea.phenomenal.chessboard

# ==============================================================================
# Load Chessboard

import alinea.phenomenal.chessboard

chessboard = alinea.phenomenal.chessboard.Chessboard.read('chessboard_1')

# ==============================================================================
# Calibration
import alinea.phenomenal.calibration_model

# Create Object
calib = alinea.phenomenal.calibration_model.Calibration(
    [chessboard], (2048, 2448), verbose=True)

# Do Calibration
cam_params, chessboard_params = calib.find_model_parameters()

cam_params.write('camera_parameters')
chessboard_params.write('chessboard_parameters')

# =============================================================================
# Viewing
import alinea.phenomenal.result_viewer

data_directory = '../../local/CHESSBOARD_1/'

projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

# Load files
files_path = glob.glob(data_directory + '*.png')
print files_path
angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_path)
print angles

for i in range(len(files_path)):
    img = cv2.imread(files_path[i], cv2.IMREAD_UNCHANGED)

    alinea.phenomenal.result_viewer.show_chessboard_3d_projection_on_image(
        img, angles[i],
        chessboard,
        chessboard_params,
        projection,
        name_windows=str(angles[i]))
