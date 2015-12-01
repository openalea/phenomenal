# -*- python -*-
#
#       chessboard.py : 
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

import cv2
import glob

import alinea.phenomenal.chessboard

# ==============================================================================

data_directory = '../local/CHESSBOARD_1/'

# Load files
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('sv_')[1]).split('.png')[0]), files_path)

image_path = dict()
for i in range(len(files_path)):
    image_path[angles[i]] = files_path[i]

# Define Chessboard size
chessboard = alinea.phenomenal.chessboard.Chessboard(47, (8, 6))

# Load image and find chessboard corners in each image
for angle in image_path:
    img = cv2.imread(image_path[angle], cv2.IMREAD_GRAYSCALE)
    chessboard.find_and_add_corners(angle, img)

# Write
chessboard.write('chessboard_1')

# Read
chessboard = alinea.phenomenal.chessboard.Chessboard.read('chessboard_1')

