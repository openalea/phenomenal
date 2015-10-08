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
import matplotlib.cm
import numpy
import pylab

#       ========================================================================
#       Local Import
import alinea.phenomenal.segmentation_2d
import alinea.phenomenal.misc
import alinea.phenomenal.result_viewer

#       ========================================================================
#       Code


def write_segmentation_on_image(stem, leaves, segments, skeleton_image):

    # Write if number on pixel image:
    for segment in segments:
        for y, x in segment.points:
            skeleton_image[y, x] = segment.id_number

    for segment in stem.segments:
        for y, x in segment.points:
            skeleton_image[y, x] = 255

    for leaf in leaves:
        for segment in leaf.segments:
            for y, x in segment.points:
                skeleton_image[y, x] = leaf.id_number

    skeleton_image = skeleton_image.astype(numpy.uint8)

    return skeleton_image


def run_example(data_directory):
    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'skeletonize_2d/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            print pot_id, date
            for angle in images:
                if angle != -1:
                    stem, leaves, segments = alinea.phenomenal.segmentation_2d.\
                        segment_organs_skeleton_image(images[angle])

                    image = numpy.zeros(images[angle].shape)

                    img = write_segmentation_on_image(stem,
                                                      leaves,
                                                      segments,
                                                      image)

                    alinea.phenomenal.result_viewer.show_images(
                        [images[angle], img],
                        name_windows='Image & Segmentation : %d degree' % angle,
                        names_axes=['Image', 'Segmentation'],
                        color_map_axes=[matplotlib.cm.binary,
                                        compute_my_random_color_map()])

                    histogram = alinea.phenomenal.segmentation_2d.\
                        compute_inclination(stem.segments)

                    pylab.hist(histogram, 180, histtype='bar', rwidth=0.8)
                    pylab.show()


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


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
