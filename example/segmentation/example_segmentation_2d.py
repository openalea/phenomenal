# -*- python -*-
#
#       example_segmentation_2d.py :
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
import cv2
import matplotlib

#       ========================================================================
#       Local Import
from alinea.phenomenal.segmentation_2d import segment_organs_skeleton_image
from alinea.phenomenal.misc import load_images, load_files, write_images
import alinea.phenomenal.result_viewer
import matplotlib.cm


#       ========================================================================
#       Code


def run_example(data_directory):
    pot_ids = load_files(data_directory + 'skeletonize_2d/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = load_images(files, cv2.IMREAD_UNCHANGED)

            skeleton_images = example_segmentation(images)

            print pot_id, date
            for angle in skeleton_images:
                alinea.phenomenal.result_viewer.show_images(
                    [images[angle], skeleton_images[angle]],
                    name_windows='Image & Segmentation : %d degree' % angle,
                    names_axes=['Image', 'Segmentation'],
                    color_map_axes=[matplotlib.cm.binary,
                                    compute_my_random_color_map()])

            write_images(data_directory + 'segmentation_2d/',
                         files,
                         skeleton_images)


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


def example_segmentation(images):
    skeleton_images = dict()
    for angle in images:
        if angle != -1:
            skeleton_images[angle] = segment_organs_skeleton_image(images[angle])

    return skeleton_images

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
