# -*- python -*-
#
#       tools_test: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 
from mayavi import mlab
import cv2

#       =======================================================================
#       Local Import 


#       =======================================================================
#       Code

def load_images(images_path):
    images = []
    for image_name in images_path:
        im = cv2.imread(image_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        images.append(im)

    return images


def show_cube(cubes, scale_factor):
    xx = []
    yy = []
    zz = []
    ss = []
    for cube in cubes:
        xx.append(int(round(cube.center.x)))
        yy.append(int(round(cube.center.y)))
        zz.append(int(round(cube.center.z)))
        ss.append(int(round(cube.radius)))

    mlab.figure()
    mlab.points3d(xx, yy, zz, mode='cube',
                  color=(0.1, 0.7, 0.1),
                  scale_factor=scale_factor)