# -*- python -*-
#
#       calibration.py : 
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
import alinea.phenomenal.plant_1
import alinea.phenomenal.chessboard
import alinea.phenomenal.calibration_model
# ==============================================================================

chessboards_path = alinea.phenomenal.plant_1.plant_1_chessboards_path()

# Load Chessboard
chessboard_1 = alinea.phenomenal.chessboard.Chessboard.read(chessboards_path[0])
chessboard_2 = alinea.phenomenal.chessboard.Chessboard.read(chessboards_path[1])

# ==============================================================================
# Calibration

# Create Object
calibration = alinea.phenomenal.calibration_model.Calibration(
    [chessboard_1, chessboard_2], (2056, 2454), verbose=True)

# Do Calibration
cam_params, chess_params = calibration.find_model_parameters(
    number_of_repetition=5)

# ==============================================================================
# Print parameters

print cam_params
print chess_params

# ==============================================================================
# Write parameters
cam_params.write('params_camera')
chess_params[0].write('params_chessboard_1')
chess_params[1].write('params_chessboard_2')

# ==============================================================================
# Read parameters
cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
    'params_camera')

chess_params = list()
chess_params.append(alinea.phenomenal.calibration_model.
                    ChessboardModelParameters.read('params_chessboard_1'))

chess_params.append(alinea.phenomenal.calibration_model.
                    ChessboardModelParameters.read('params_chessboard_2'))

# ==============================================================================
# Compute error projection
err = alinea.phenomenal.calibration_model.compute_error_projection(
    cam_params, [chessboard_1, chessboard_2], chess_params)

print 'Error :', err

# ==============================================================================
# Viewing
import alinea.phenomenal.viewer
import cv2
import glob

data_directory = '../../local/CHESSBOARD_1/'

projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

# Load files
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_path)

for i in range(len(files_path)):
    img = cv2.imread(files_path[i], cv2.IMREAD_UNCHANGED)

    alinea.phenomenal.viewer.show_chessboard_3d_projection_on_image(
        img,
        angles[i],
        chessboard_1,
        chess_params[0],
        projection,
        name_windows=str(angles[i]))
