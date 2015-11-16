# -*- python -*-
#
#       calibration_script.py : 
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

#       ========================================================================
#       Local Import 

#       ========================================================================
#       Load Chessboard
import alinea.phenomenal.chessboard

chessboard_1 = alinea.phenomenal.chessboard.Chessboard.read(
    'chessboard_1')

chessboard_2 = alinea.phenomenal.chessboard.Chessboard.read(
    'chessboard_2')

#       ========================================================================
#       Load image
import cv2
import glob

data_directory = '../../local/CHESSBOARD_ELCOM_5/'

# Load files
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('side_')[1]).split('.png')[0]), files_path)

image_path = dict()
for i in range(len(files_path)):
    image_path[angles[i]] = files_path[i]

    img = cv2.imread(image_path[angles[i]], cv2.IMREAD_GRAYSCALE)

    size_image = img.shape

import alinea.phenomenal.result_viewer
import alinea.phenomenal.calibration_model

calib = alinea.phenomenal.calibration_model.Calibration()
calib.find_model_parameters_2(chessboard_1, chessboard_2, (2048, 2448))
calib.write_calibration('my_calibration')

calib = alinea.phenomenal.calibration_model.Calibration.read_calibration(
    'my_calibration')


for angle in image_path:
    img = cv2.imread(image_path[angle], cv2.IMREAD_UNCHANGED)

    alinea.phenomenal.result_viewer.show_chessboard_3d_projection_on_image(
        img, angle, chessboard_1, calib, name_windows=str(angle))
# Define size of chessboard

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    pass