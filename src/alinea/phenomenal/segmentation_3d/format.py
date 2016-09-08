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
from __future__ import print_function, absolute_import, division

import os
import csv
import collections
# ==============================================================================


def write_labeled_voxels_to_csv(filename, labeled_voxels, voxel_size):

    if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
            filename))):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'wb') as f:
        c = csv.writer(f)

        c.writerow(['x_coord', 'y_coord', 'z_coord', 'voxel_size', 'label'])

        for label in labeled_voxels:
            for x, y, z in labeled_voxels[label]:
                c.writerow([x, y, z, voxel_size, label])


def read_labeled_voxels_from_csv(filename):

    labeled_voxels = collections.defaultdict(list)
    with open(filename, 'rb') as f:
        reader = csv.reader(f)

        next(reader)
        x, y, z, vs, label = next(reader)
        labeled_voxels[label].append((float(x), float(y), float(z)))

        voxel_size = float(vs)

        for x, y, z, vs, label in reader:
            labeled_voxels[label].append((float(x), float(y), float(z)))

        return labeled_voxels, voxel_size


def write_labeled_skeleton_path_to_csv(filename, labeled_skeleton_path):

    if (os.path.dirname(filename) and not os.path.exists(os.path.dirname(
            filename))):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'wb') as f:
        c = csv.writer(f)

        c.writerow(['index', 'x_coord', 'y_coord', 'z_coord', 'label'])

        for label in labeled_skeleton_path:
            for i, (x, y, z) in enumerate(labeled_skeleton_path[label]):
                c.writerow([i, x, y, z, label])


def read_labeled_skeleton_path_from_csv(filename):

    labeled_skeleton_path = collections.defaultdict(list)
    with open(filename, 'rb') as f:
        reader = csv.reader(f)

        next(reader)
        i, x, y, z, label = next(reader)
        labeled_skeleton_path[label].append((float(x), float(y), float(z)))

        for x, y, z, vs, label in reader:
            labeled_skeleton_path[label].append((float(x), float(y), float(z)))

        return labeled_skeleton_path
