# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os
import re
import cv2
import csv
import collections
# ==============================================================================


def save_matrix_to_stack_image(matrix, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    xl, yl, zl = matrix.shape
    for i in range(zl):
        mat = matrix[:, :, i] * 255
        cv2.imwrite(folder_name + '%d.png' % i, mat)


def write_to_xyz(filename, voxel_centers):

    if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
            filename))):
        os.makedirs(os.path.dirname(filename))

    f = open(filename, 'wb')
    for x, y, z in voxel_centers:
        f.write("%f %f %f \n" % (x, y, z))
    f.close()


def read_from_xyz(filename):
    voxel_centers = list()
    with open(filename, 'r') as f:
        for line in f:
            point_3d = re.findall(r'[-0-9.]+', line)

            x = float(point_3d[0])
            y = float(point_3d[1])
            z = float(point_3d[2])

            voxel_centers.append((x, y, z))
    f.close()

    return voxel_centers


def write_to_csv(filename, voxel_centers, voxel_size):

    if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
            filename))):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'wb') as f:
        c = csv.writer(f)

        c.writerow(['x_coord', 'y_coord', 'z_coord', 'voxel_size'])

        for x, y, z in voxel_centers:
            c.writerow([x, y, z, voxel_size])


def read_from_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)

        next(reader)
        x, y, z, vs = next(reader)

        voxel_size = float(vs)

        voxel_centers = list()
        voxel_centers.append((float(x), float(y), float(z)))

        for x, y, z, vs in reader:
            voxel_centers.append((float(x), float(y), float(z)))

        return voxel_centers, voxel_size


def write_to_csv_with_label(filename, label_voxel_centers, voxel_size):

    if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
            filename))):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'wb') as f:
        c = csv.writer(f)

        c.writerow(['x_coord', 'y_coord', 'z_coord', 'voxel_size', 'label'])

        for label in label_voxel_centers:
            for x, y, z in label_voxel_centers[label]:
                c.writerow([x, y, z, voxel_size, label])

def read_from_csv_with_label(filename):

    label_voxel_centers = collections.defaultdict(list)
    with open(filename, 'rb') as f:
        reader = csv.reader(f)

        next(reader)
        x, y, z, vs, label = next(reader)
        label_voxel_centers[label].append((float(x), float(y), float(z)))

        voxel_size = float(vs)

        for x, y, z, vs, label in reader:
            label_voxel_centers[label].append((float(x), float(y), float(z)))

        return label_voxel_centers, voxel_size

