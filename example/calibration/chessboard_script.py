# -*- python -*-
#
#       chessboard_script.py : 
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
#       Code

#       ========================================================================
#       External Import
import cv2
import glob


#       ========================================================================
#       Local Import
import alinea.phenomenal.chessboard
#       ========================================================================
#       Code
#
data_directory = '../../local/CHESSBOARD_ELCOM_6_2/'

# Load files
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('side_')[1]).split('.png')[0]), files_path)

image_path = dict()
for i in range(len(files_path)):
    image_path[angles[i]] = files_path[i]

# Define Chessboard size
chessboard = alinea.phenomenal.chessboard.Chessboard(47, (8, 6))

# Load image and find chessboard corners in each image
chessboard_corners = dict()
for angle in image_path:
    print angle
    img = cv2.imread(image_path[angle], cv2.IMREAD_GRAYSCALE)
    chessboard.find_and_add_corners(angle, img)

chessboard.write('chessboard_elcom_6_2')
