# -*- python -*-
#
#       example_tools.py.py : 
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
import re
import cv2


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


def read_xyz(file):
    points_3d = list()
    with open(file, 'r') as f:
        radius = float(f.readline())

        for line in f:
            point_3d = re.findall(r'[-0-9.]+', line)

            x = float(point_3d[0])
            y = float(point_3d[1])
            z = float(point_3d[2])

            points_3d.append((x, y, z))

    f.close()

    return points_3d, radius


def load_xyz_files(data_directory):
    images_names = glob.glob(data_directory + '*.xyz')

    pot_ids = dict()
    for i in range(len(images_names)):

        pot_id = images_names[i].split('\\')[-1].split('_')[0]
        if pot_id not in pot_ids:
            pot_ids[pot_id] = dict()

        date = images_names[i].split(' ')[0].split('_')[-1]

        pot_ids[pot_id][date] = images_names[i]

    return pot_ids


def write_points_3d(points_3d, radius, data_directory, name_file):
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    f = open(data_directory + name_file + '.xyz', 'w')

    if len(points_3d) > 0:
        f.write("%f\n" % radius)

    for point_3d in points_3d:
        x, y, z = point_3d
        f.write("%f %f %f \n" % (x, y, z))

    f.close()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
