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
from networkx.algorithms.assortativity import neighbor_degree

__revision__ = ""

#       =======================================================================
#       External Import
import numpy as np
from collections import deque

#       =======================================================================
#       Local Import 

#       =======================================================================
#       Code

def give_me_first_neighbor(skeleton_image, j, i):

    neighbors = list()
    for jj in [-1, 0, 1]:
        for ii in [-1, 0, 1]:
            if jj == 0 and ii == 0:
                continue

            pix = skeleton_image[j + jj, i + ii]
            #Nothing
            if pix == 0:
                continue
            #Already tagged
            if pix < 255:
                continue

            neighbors.append((j + jj, i + ii))

    return neighbors


def give_me_neighbor(skeleton_image, j, i, label_number):

    number = 0
    i_next = -1
    j_next = -1

    for jj in [-1, 0, 1]:
        for ii in [-1, 0, 1]:
            if jj == 0 and ii == 0:
                continue

            pix = skeleton_image[j + jj, i + ii]

            if pix == 0:
                continue

            if pix < label_number:
                return -1, -1

            if pix == 255:
                number += 1
                i_next = i + ii
                j_next = j + jj

            if number == 2:
                return -2, -2

    return j_next, i_next


def get_closest_label(label, labels):

    closest_label = list()

    for r in range(20):
        for lab in labels:
            if lab is not label:
                for j, i in label['index']:
                    for jj, ii in lab['index']:
                        if -r <= j - jj <= r and -r <= i - ii <= r:
                            closest_label.append((lab, r))
        if closest_label is not []:
            break

    return closest_label


def get_first_closest_label(label, labels):
    for r in range(20):
        for lab in labels:
            if lab is not label:
                for j, i in label['index']:
                    for jj, ii in lab['index']:
                        if -r <= j - jj <= r and -r <= i - ii <= r:
                            return lab, r

    return None, None


def get_closest_label(label, labels, r):
    for lab in labels:
        if lab is not label:
            for j, i in label['index']:
                for jj, ii in lab['index']:
                    if -r <= j - jj <= r and -r <= i - ii <= r:
                        return lab

    return None


def transfer_label(label_src, label_dest):
    for j, i in label_src['index']:
        label_dest['index'].append((j, i))

    return label_dest


class Segment(object):
    def __init__(self, id_number):
        self.id_number = id_number
        self.first_id_number = id_number
        self.points = list()
        self.first_point = -1
        self.last_point = -1

    def get_size(self):
        return len(self.points)


class Trunk(object):
    def __init__(self):
        self.segments = list()

    def global_position(self):
        y_mean, x_mean = (0, 0)
        for segment in self.segments:
            for y, x in segment.points:
                y_mean += y
                x_mean += x

        return y_mean, x_mean


    def get_height(self):
        y_min = 5000
        y_max = -5000

        for segment in self.segments:
            for y, x in segment.points:
                y_min = min(y_min, y)
                y_max = max(y_max, y)

        return y_max - y_min


    def get_width(self):
        x_min = 5000
        x_max = -5000

        for segment in self.segments:
            for y, x in segment.points:
                x_min = min(x_min, x)
                x_max = max(x_max, x)

        return x_max - x_min


    def is_in_trunk(self, segment):
        for trunk_segment in self.segments:
            if trunk_segment is segment:
                return True

        return False

    def print_value(self):
        print "Number of segment : ", len(self.segments)
        print "Height : ", self.get_height()
        print "Width : ", self.get_width()
        print "Global position : ", self.global_position()

        for segment in self.segments:
            for y, x in segment.points:
                print y, x


def neighbors_value(skeleton_image, y, x):
    values = list()
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if j == 0 and i == 0:
                continue

            values.append(skeleton_image[y + j, x + i])

    return values


def neighbors_is_tagged(skeleton_image, j, i):

    values = neighbors_value(skeleton_image, j, i)
    for value in values:
        if value == -1:
            return True

    return False


def neighbors_valid_index(skeleton_image, y, x):

    neighbors_index = list()
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if j == 0 and i == 0:
                continue

            pixel = skeleton_image[y + j, x + i]

            # Continue, pixel is black, no organs
            if pixel == 0:
                continue

            # Continue, pixel is already tagged
            if pixel == -1:
                continue

            neighbors_index.append((y + j, x + i))

    return neighbors_index


def next_neighbors(skeleton_image, y, x):

    tagged_number = 0
    valid_number = 0

    y_next = -1
    x_next = -1

    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if j == 0 and i == 0:
                continue

            pixel = skeleton_image[y + j, x + i]
            # Continue, pixel is black, no organs
            if pixel == 0:
                continue

            # Continue, pixel is already tagged
            if pixel == -1:
                tagged_number += 1

            if pixel == 255:
                valid_number += 1

                y_next = y + j
                x_next = x + i

            if valid_number > 1 or tagged_number > 1:
                return -1, -1

    return y_next, x_next


def segment_skeleton(skeleton_image):
    h, l = np.shape(skeleton_image)
    segments = list()
    id_number = 1
    for j in xrange(h):
        for i in xrange(l):
            pixel = skeleton_image[j, i]

            # Continue, pixel is black, no organs
            if pixel == 0:
                continue

            # Continue, pixel is already tagged
            if pixel == -1:
                continue

            neighbors_index = neighbors_valid_index(skeleton_image, j, i)
            number_of_valid_neighbors = len(neighbors_index)

            if not (1 <= number_of_valid_neighbors <= 2):
                continue

            # Neighbors of pixel is tagged, so its considering as point junction
            if number_of_valid_neighbors == 2:
                if neighbors_is_tagged(skeleton_image, j, i) is True:
                    # We create a new segments
                    segment = Segment(id_number)
                    segment.points.append((j, i))
                    segment.first_point = (j, i)
                    segment.last_point = (j, i)
                    segments.append(segment)
                    skeleton_image[j, i] = -1
                    id_number += 1
                    print id_number
                    continue

            # We create a new segments
            segment = Segment(id_number)
            segment.points.append((j, i))
            segment.first_point = (j, i)
            segment.last_point = (j, i)
            segments.append(segment)
            skeleton_image[j, i] = -1
            id_number += 1
            print id_number

            y, x = neighbors_index[0]
            while y > -1 and x > -1:
                segment.points.append((y, x))
                segment.last_point = (y, x)
                skeleton_image[y, x] = -1
                y, x = next_neighbors(skeleton_image, y, x)

            if number_of_valid_neighbors == 2:
                y, x = neighbors_index[1]
                while y > -1 and x > -1:
                    segment.points.append((y, x))
                    segment.first_point = (y, x)
                    skeleton_image[y, x] = -1
                    y, x = next_neighbors(skeleton_image, y, x)

    return segments


def segment_organs_skeleton_image(skeleton_image):

    skeleton_image = skeleton_image.astype(np.int)

    segments = segment_skeleton(skeleton_image)

    candidates_trunc = list()
    for segment in segments:
        size_segments = len(segment.points)

        if size_segments <= 4:
            candidates_trunc.append(segment)
            continue

        yb, xb = segment.first_point
        ya, xa = segment.last_point
        yo, xo = (yb, xa)

        if xa == xb:
            candidates_trunc.append(segment)
            continue

        if ya == yb:
            continue

        import math

        AB = math.sqrt((xa - xb)**2 + (ya - yb)**2)
        AO = math.sqrt((xa - xo)**2 + (ya - yo)**2)
        OB = math.sqrt((xo - xb)**2 + (yo - yb)**2)

        alpha = math.acos((AO**2 + AB**2 - OB**2) / (2.0 * AO * AB))
        alpha = alpha * 180.0 / np.pi

        if 0 <= alpha <= 25:
            candidates_trunc.append(segment)
            continue

    r = 5
    for segment_1 in candidates_trunc:
        for segment_2 in candidates_trunc:
            if segment_2.id_number != segment_1.id_number:
                for j, i in segment_1.points:
                    for jj, ii in segment_2.points:
                        if -r <= j - jj <= r and -r <= i - ii <= r:
                            segment_2.id_number = segment_1.id_number


    trunks = dict()
    for segment in candidates_trunc:
        if segment.id_number not in trunks:
            trunks[segment.id_number] = Trunk()

        trunks[segment.id_number].segments.append(segment)


    final_trunk = None
    max_height = 0
    for id in trunks.keys():
        height = trunks[id].get_height()
        if height > max_height:
            max_height = height
            final_trunk = trunks[id]


    final_trunk.print_value()

    for segment in candidates_trunc:
        if final_trunk.is_in_trunk(segment) is False:
            segment.id_number = segment.first_id_number



    for segment in segments:
        for y, x in segment.points:
            skeleton_image[y, x] = segment.id_number

    return skeleton_image


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
