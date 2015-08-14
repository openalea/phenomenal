# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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
import cv2
import glob
import matplotlib
from pylab import *

#       =======================================================================
#       Local Import
import alinea.phenomenal.skeletonize as skeletonize
import alinea.phenomenal.segmentation as segmentation


#       =======================================================================
#       Code

def compute_my_random_color_map():
    cdict = dict()
    cdict['red'] = ((0., 0., 0.),)
    cdict['green'] = ((0., 0., 0.),)
    cdict['blue'] = ((0., 0., 0.),)
    import random

    def random_color(i):
        return ((float(i / 100.0),
                 random.uniform(0.1, 1.0),
                 random.uniform(0.1, 1.0)),)

    for i in range(0, 100):
        cdict['red'] = cdict['red'] + random_color(i)
        cdict['green'] = cdict['green'] + random_color(i)
        cdict['blue'] = cdict['blue'] + random_color(i)

    cdict['red'] = cdict['red'] + ((1, 1, 1),)
    cdict['green'] = cdict['green'] + ((1, 1, 1),)
    cdict['blue'] = cdict['blue'] + ((1, 1, 1),)

    my_random_color_map = matplotlib.colors.LinearSegmentedColormap(
        'my_colormap', cdict, 256)

    return my_random_color_map



def show_image_and_skeleton(image, skeleton):

    my_random_color_map = compute_my_random_color_map()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    ax1.imshow(image, cmap=my_random_color_map, interpolation='nearest')
    ax1.axis('off')

    ax2.imshow(skeleton, cmap=my_random_color_map, interpolation='nearest')
    # ax2.contour(image, [0.5], colors='w')
    ax2.axis('off')

    fig.subplots_adjust(
        hspace=0.01, wspace=0.01, top=1, bottom=0, left=0, right=1)

    plt.show()


def test_skeletonize():
    data_directory = "../../local/data/tests/Samples_binarization_2/"
    images_path = glob.glob(data_directory + '*.png')

    images = map(lambda x: cv2.imread(x, cv2.IMREAD_GRAYSCALE), images_path)

    for image in images:
        skeleton = skeletonize.skeletonize_image_skimage(image)
        skeleton = segmentation.segment_organs_skeleton_image(skeleton)

        show_image_and_skeleton(image, skeleton)

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
    test_skeletonize()
