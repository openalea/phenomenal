# -*- python -*-
#
#       chessboard_script_2.py : 
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
#       Import
import glob
import cv2
import numpy.linalg
import matplotlib.pyplot
import alinea.phenomenal.chessboard
import alinea.phenomenal.result_viewer

#       ========================================================================
#       Code
#
data_directory = '../../local/CHESSBOARD_ELCOM_6_2/'

# Load files
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('_side_')[1]).split('.png')[0]), files_path)

image_path = dict()
for i in range(len(files_path)):
    image_path[angles[i]] = files_path[i]

# Load chessboard
chessboard = alinea.phenomenal.chessboard.Chessboard.read(
    'chessboard_elcom_6_2')

# Compute distance
angle = 285
sum_distance_1 = 0.0
print 'Angle : ', angle
corners = chessboard.corners_points[angle]

sum_distance = 0
for i in range(6):
    pt_1 = corners[0 + i * 8]
    pt_2 = corners[7 + i * 8]

    distance_1_2 = numpy.linalg.norm(pt_1 - pt_2)
    sum_distance_1 += distance_1_2

    # Viewing point
    img = cv2.imread(image_path[angle], cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    corners = corners.astype(int)
    img[pt_1[0, 1], pt_1[0, 0]] = [255, 0, 0]
    img[pt_2[0, 1], pt_2[0, 0]] = [0, 255, 0]

    matplotlib.pyplot.imshow(img)
    matplotlib.pyplot.show()

sum_distance_1 /= 6.0

mean_distance_7_square = sum_distance_1 / 7.0

print 'Mean distance 7 square : ', mean_distance_7_square

ratio_pixel = 47.0 / mean_distance_7_square

print 'Ratio mm / pixel : ', ratio_pixel
print 'Distance 40 pixel to mm : ', 40.0 * ratio_pixel