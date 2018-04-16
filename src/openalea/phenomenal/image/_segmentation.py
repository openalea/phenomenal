# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import math
import numpy
# ==============================================================================


class Segment(object):
    def __init__(self, id_number, first_point):
        self.id_number = id_number
        self.first_id_number = id_number
        self.points = list()
        self.points.append(first_point)
        self.first_point = first_point
        self.last_point = first_point

    def get_size(self):
        return len(self.points)

    def global_position(self):
        y_mean, x_mean = (0, 0)
        for y, x in self.points:
            y_mean += y
            x_mean += x

        return y_mean / len(self.points), x_mean / len(self.points)

    def get_vector(self):
        ya, xa = self.points[0]
        yb, xb = self.points[-1]

        return xa - xb, ya - yb

    def compute_inclination(self, step=10):

        result = list()

        my_range = range(1, len(self.points) - step, step)
        if len(my_range) < 2:
            return result

        for i in my_range:
            ya, xa = self.points[i]
            yb, xb = self.points[i + step]

            diff_x = xa - xb
            diff_y = ya - yb

            norm = math.sqrt(diff_x ** 2 + diff_y ** 2)
            inclination = math.atan2(math.fabs(diff_y), math.fabs(diff_x))
            inclination = inclination / math.pi * 180.0

            result.append((inclination, norm))

        return result

    def compute_angle_orientation(self):

        yb, xb = self.first_point
        ya, xa = self.last_point
        yo, xo = (yb, xa)

        if xa == xb:
            return 0

        if ya == yb:
            return 180

        ab = math.sqrt((xa - xb) ** 2 + (ya - yb) ** 2)
        ao = math.sqrt((xa - xo) ** 2 + (ya - yo) ** 2)
        ob = math.sqrt((xo - xb) ** 2 + (yo - yb) ** 2)

        alpha = math.acos((ao ** 2 + ab ** 2 - ob ** 2) / (2.0 * ao * ab))
        alpha = alpha * 180.0 / numpy.pi

        return alpha


class Organ(object):
    def __init__(self):
        self.segments = list()
        self.id_number = None

    def global_position(self):
        y_mean, x_mean = (0, 0)
        for segment in self.segments:
            for y, x in segment.points:
                y_mean += y
                x_mean += x

        return y_mean / len(self.segments), x_mean / len(self.segments)

    def get_height(self):
        y_min = numpy.float('inf')
        y_max = - numpy.float('inf')

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

    def is_in(self, segment):
        for organ_segment in self.segments:
            if organ_segment is segment:
                return True

        return False

    def is_close(self, segment, radius=1):
        for organ_segment in self.segments:
            for y, x in organ_segment.points:
                for yy, xx in segment.points:
                    if (-radius <= y - yy <= radius and
                                    -radius <= x - xx <= radius):
                        return True

        return False

    def print_value(self):
        print("Number of segment : ", len(self.segments))
        print("Height : ", self.get_height())
        print("Width : ", self.get_width())
        print("Global position : ", self.global_position())


class Stem(Organ):
    def __init__(self):
        Organ.__init__(self)


class Leaf(Organ):
    def __init__(self):
        Organ.__init__(self)


# ==============================================================================
# Segments plants


def neighbors_is_tagged(skeleton_image, y, x):
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            if j == 0 and i == 0:
                continue

            if skeleton_image[y + j, x + i] == -1:
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
    h, l = numpy.shape(skeleton_image)

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

            # We create a new segments
            segment = Segment(id_number, (j, i))
            # We tag te pixel on skeleton image
            skeleton_image[j, i] = -1

            # If possible next neighbors is 2 and furthermore 1 other pixel
            # is tagged, is a points of junction between 3 segment so we pass
            # the point
            if not (number_of_valid_neighbors == 2 and
                            neighbors_is_tagged(skeleton_image, j, i) is True):

                if len(neighbors_index) > 0:
                    y, x = neighbors_index[0]
                    while y > -1 and x > -1:
                        segment.points.append((y, x))
                        skeleton_image[y, x] = -1
                        y, x = next_neighbors(skeleton_image, y, x)

                    segment.last_point = segment.points[-1]

                if len(neighbors_index) > 1:
                    y, x = neighbors_index[0]
                    while y > -1 and x > -1:
                        segment.points.insert(0, (y, x))
                        skeleton_image[y, x] = -1
                        y, x = next_neighbors(skeleton_image, y, x)

                    segment.first_point = segment.points[0]

            # Add segment to the list
            segments.append(segment)
            # Increment id number
            id_number += 1

    return segments


# ==============================================================================
# Segment Stem

def compute_orientation(vector1, vector2):
    x1, y1 = vector1
    x2, y2 = vector2

    if (x1 == 0.0 and y1 == 0.0) or (x2 == 0.0 and y2 == 0.0):
        return 90

    result = numpy.dot((x1, y1), (x2, y2)) / (
        numpy.linalg.norm((x1, y1)) * numpy.linalg.norm((x2, y2)))

    result = round(result, 5)
    return math.acos(result) * 180.0 / math.pi


def build_stem_2(segments):

    print("Number of segments : ", len(segments))

    list_list = list()
    for segment_1 in segments[:]:

        list_candidate = list()
        list_candidate.append(segment_1)

        vector_1 = segment_1.get_vector()
        for segment_2 in segments[:]:
            if segment_1 is not segment_2:
                vector_2 = segment_2.get_vector()
                angle = compute_orientation(vector_1, vector_2)
                if 0 <= angle <= 20 or 160 <= angle <= 180:
                    list_candidate.append(segment_2)

        img = numpy.zeros((2454, 2056)).astype(numpy.uint8)
        for segment in list_candidate:
            for y, x in segment.points:
                img[y, x] = 255

        list_list.append(list_candidate)

    radius = 10
    stems = list()
    for list_candidate in list_list:

        list_of_possible_segment = list_candidate

        while list_of_possible_segment:

            segment = list_of_possible_segment.pop()
            stem = Stem()
            stem.segments.append(segment)
            stem.id_number = segment.id_number

            stop = False
            while stop is False:
                stop = True

                for seg_left in list_of_possible_segment[:]:
                    if stem.is_close(seg_left, radius):
                        stem.segments.append(seg_left)
                        list_of_possible_segment.remove(seg_left)
                        stop = False

            stems.append(stem)

    stem_choose = None
    max_height = 0
    for stem in stems:
        height = stem.get_height()
        if height > max_height:
            max_height = height
            stem_choose = stem

    # for segment in segments[:]:
    #     if stem_choose.is_in(segment):
    #         segments.remove(segment)

    return stem_choose, segments


def get_possible_stem_segment(segments):
    possible_stem_segment = list()
    for segment in segments:
        size_segments = len(segment.points)

        if size_segments <= 4:
            possible_stem_segment.append(segment)
            continue

        alpha = segment.compute_angle_orientation()

        if 0 <= alpha <= 25:
            possible_stem_segment.append(segment)
            continue

    print("Candidates stem : ", len(possible_stem_segment))

    return possible_stem_segment


def build_stem(possible_stem_segment):
    radius = 5
    stems = list()
    while possible_stem_segment:
        segment = possible_stem_segment.pop()

        stem = Stem()
        stem.segments.append(segment)
        stem.id_number = segment.id_number
        stems.append(stem)

        stop = False
        while stop is False:
            stop = True
            for seg_left in possible_stem_segment[:]:
                if stem.is_close(seg_left, radius):
                    stem.segments.append(seg_left)
                    possible_stem_segment.remove(seg_left)
                    stop = False

    stem_choose = None
    max_height = 0
    for stem in stems:
        height = stem.get_height()
        if height > max_height:
            max_height = height
            stem_choose = stem

    return stem_choose


def segment_stem(segments):
    # possible_stem_segment = get_possible_stem_segment(segments)
    #
    # stem = build_stem(possible_stem_segment)

    stem, segments = build_stem_2(segments)

    return stem


# ==============================================================================
# Segment Leaves


def segment_leaves(segments, stem):
    leaves = list()

    def get_first_organs():
        for segment in segments:
            if stem.is_close(segment):
                return segment
        return None

    while True:
        seg = get_first_organs()

        if seg is None:
            break
        else:
            segments.remove(seg)

            my_leaf = Leaf()
            my_leaf.segments.append(seg)
            my_leaf.id_number = seg.id_number

            stop = False
            while stop is False:
                stop = True
                for seg_left in segments[:]:

                    if my_leaf.is_close(seg_left, 5):
                        my_leaf.segments.append(seg_left)
                        segments.remove(seg_left)
                        stop = False

            leaves.append(my_leaf)

    print("Number of leaf : ", len(leaves))

    return leaves, segments


# ==============================================================================
# Segment Organs


def compute_inclination(segments):
    histogram = list()
    for segment in segments:
        angles_inclinations = segment.compute_inclination(step=5)

        for angle in angles_inclinations:
            histogram.append(angle[0])

    return numpy.array(histogram)


def segment_organs_skeleton_image(skeleton_image):
    # Transform skeleton image as type int for tag pixel to -1
    skeleton_image = skeleton_image.astype(numpy.int)

    # Get the segments list of the skeleton image
    segments = segment_skeleton(skeleton_image)

    # Get the stem segments
    stem = segment_stem(segments)

    # Remove stem segment from the segments list
    segments[:] = [segment
                   for segment in segments
                   if not stem.is_in(segment) is True]

    # compute_inclination(stem.segments)

    leaves, segments = segment_leaves(segments, stem)

    return stem, leaves, segments
