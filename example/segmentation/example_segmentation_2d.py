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
import glob
import os
import cv2
import matplotlib
import matplotlib.pyplot as plt

#       ========================================================================
#       Local Import
from alinea.phenomenal.segmentation_2d import segment_organs_skeleton_image

#       ========================================================================
#       Code

def load_files(data_directory):

    images_names = glob.glob(data_directory + '*.png')

    pot_ids = dict()
    for i in range(len(images_names)):

        pot_id = images_names[i].split('\\')[-1].split('_')[0]
        if pot_id not in pot_ids:
            pot_ids[pot_id] = dict()

        date = images_names[i].split(' ')[0].split('_')[-1]
        # data = 10
        if date not in pot_ids[pot_id]:
            pot_ids[pot_id][date] = dict()

        result = images_names[i].split('_sv')
        if len(result) == 2:
            angle = result[1].split('.png')[0]
        else:
            result = images_names[i].split('_tv')
            if len(result) == 2:
                angle = -1
            else:
                continue

        pot_ids[pot_id][date][int(angle)] = images_names[i]

    return pot_ids


def load_images(files, cv2_flag):
    images = dict()
    for angle in files:
        images[angle] = cv2.imread(files[angle], flags=cv2_flag)

    return images


def write_images(data_directory, files, images):

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    for angle in images:

        path = files[angle]
        filename = path.split('\\')[-1]
        path = data_directory + filename

        cv2.imwrite(path, images[angle])


def run_example(data_directory):
    pot_ids = load_files(data_directory + 'skeletonize_2d/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            if pot_id == 595:
                files = pot_ids[pot_id][date]

                images = load_images(files, cv2.IMREAD_UNCHANGED)

                skeleton_images = example_segmentation(images)

                # print pot_id, date
                # for angle in skeleton_images:
                #     show_images([images[angle], skeleton_images[angle]],
                #                 str(angle))

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


def example_segmentation(images):
    skeleton_images = dict()
    for angle in images:
        if angle != -1:
            skeleton_images[angle] = segment_organs_skeleton_image(images[angle])

        if angle == 120:
            show_image_and_skeleton(images[angle], skeleton_images[angle])

    return skeleton_images

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    # run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    run_example('../../local/Figure_3D/')
