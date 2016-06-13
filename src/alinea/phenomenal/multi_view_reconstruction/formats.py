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

# ==============================================================================

def save_matrix_to_stack_image(matrix, folder_name, ):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    xl, yl, zl = matrix.shape
    print xl, yl, zl
    for i in range(zl):
        mat = matrix[:, :, i] * 255
        cv2.imwrite(folder_name + '%d.png' % i, mat)


def write_xyz(points_3d, file_path):
    path_directory, file_name = os.path.split(file_path)

    if path_directory.strip() and not os.path.exists(path_directory):
        os.makedirs(path_directory)

    f = open(file_path + '.xyz', 'w')

    for point_3d in points_3d:
        x, y, z = point_3d
        f.write("%f %f %f \n" % (x, y, z))

    f.close()


def read_xyz(file_path):
    points_3d = list()
    with open(file_path + '.xyz', 'r') as f:
        for line in f:
            point_3d = re.findall(r'[-0-9.]+', line)

            x = float(point_3d[0])
            y = float(point_3d[1])
            z = float(point_3d[2])

            points_3d.append((x, y, z))

    f.close()

    return points_3d


def write_to_csv(voxel_centers, voxel_size, file_path):
    with open(file_path, 'wb') as f:
        c = csv.writer(f)

        c.writerow(['x_coord', 'y_coord', 'z_coord', 'voxel_size'])

        for x, y, z in voxel_centers:
            c.writerow([x, y, z, voxel_size])


def read_from_csv(file_path):
    with open(file_path, 'rb') as f:
        reader = csv.reader(f)

        next(reader)
        x, y, z, vs = next(reader)

        voxel_size = float(vs)

        voxel_centers = list()
        voxel_centers.append((float(x), float(y), float(z)))

        for x, y, z, vs in reader:
            voxel_centers.append((float(x), float(y), float(z)))

        return voxel_centers, voxel_size
