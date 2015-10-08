# -*- python -*-
#
#       segmentation_3d.py :
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
import math

import numpy


#       ========================================================================
#       Class


class Segment(object):
    def __init__(self, points):
        self.points = list()
        self.points.append(points[0])
        self.points.append(points[1])
        self.component = list()
        self.component.append(points[2])

    def find_segment(self, vectors, segments):

        point = self.points[0]

        save_point_equal = None
        save_point = None
        save_vector = None

        number_of_closest_point = 0
        for vector in vectors:
            if point == vector[0]:
                number_of_closest_point += 1
                save_point_equal = vector[0]
                save_point = vector[1]

            if point == vector[1]:
                number_of_closest_point += 1
                save_point_equal = vector[1]
                save_point = vector[0]
                save_vector = vector

        if not self.point_is_in_segments(save_point_equal, segments):
            if number_of_closest_point == 1:
                self.points.insert(0, save_point)
                self.component.append(save_vector[2])
                vectors.remove(save_vector)
                return True

        point = self.points[-1]

        save_point_equal = None
        save_point = None
        save_vector = None

        number_of_closest_point = 0
        for vector in vectors:
            if point == vector[0]:
                number_of_closest_point += 1
                save_point_equal = vector[0]
                save_point = vector[1]
                save_vector = vector

            if point == vector[1]:
                number_of_closest_point += 1
                save_point_equal = vector[1]
                save_point = vector[0]
                save_vector = vector

        if not self.point_is_in_segments(save_point_equal, segments):
            if number_of_closest_point == 1:
                self.points.append(save_point)
                self.component.append(save_vector[2])
                vectors.remove(save_vector)
                return True

        return False

    def point_is_in_segments(self, point, segments):
        for segment in segments:
            if segment is not self:
                if segment.is_in(point):
                    return True
        return False

    def is_in(self, point):
        for pt in self.points:
            if pt == point:
                return True
        return False

    def get_max_z_point(self):
        max_z_point = [0, 0, - numpy.float('inf')]

        for point in self.points:
            if point[2] > max_z_point[2]:
                max_z_point = point

        return max_z_point

    def get_min_z_point(self):
        min_z_point = [0, 0, numpy.float('inf')]

        for point in self.points:
            if point[2] < min_z_point[2]:
                min_z_point = point

        return min_z_point

    def get_angle_orientation(self):

        a = self.points[-1]
        b = self.points[0]
        c = [b[0], b[1], a[2]]

        ab = [a[0] - b[0],
              a[1] - b[1],
              a[2] - b[2]]

        bc = [c[0] - b[0],
              c[1] - b[1],
              c[2] - b[2]]

        angle_orientation = math.atan2(numpy.linalg.norm(numpy.cross(ab, bc)),
                                       numpy.dot(ab, bc))

        angle_orientation = angle_orientation * 180.0 / numpy.pi

        return angle_orientation

    def is_close(self, segment):
        for point_1 in self.points:
            for point_2 in segment.points:
                if not point_1 == point_2:
                    return False
        return True

    def get_vector(self):
        a = self.points[-1]
        b = self.points[0]

        ab = [b[0] - a[0],
              b[1] - a[1],
              b[2] - a[2]]

        return ab


class Organ(object):
    def __init__(self, segment):
        self.segments = list()
        self.segments.append(segment)

    def is_close(self, segment):
        for organ_segment in self.segments:
            for organ_point in organ_segment.points:
                for point in segment.points:
                    if organ_point == point:
                        return True
        return False

    def is_position_close_2(self, point, radius=5):
        for organ_segment in self.segments:
            for component in organ_segment.component:
                for point_component in component:
                    distance = numpy.linalg.norm(point - point_component)

                    if distance <= radius:
                        return True

        return False

    def is_position_close(self, point, radius=5):
        for organ_segment in self.segments:
            for organ_point in organ_segment.points:
                distance = numpy.linalg.norm(point - organ_point)

                if distance <= radius:
                    return True

        return False

    def get_height(self):
        z_min = numpy.float('inf')
        z_max = - numpy.float('inf')

        for segment in self.segments:
            z_min = min(segment.get_min_z_point()[2], z_min)
            z_max = max(segment.get_max_z_point()[2], z_max)

        print z_max, z_min
        return z_max - z_min

    def is_in(self, segment):
        for stem_segment in self.segments:
            if stem_segment is segment:
                return True
        return False


class Stem(Organ):
    def __init__(self, segment):
        Organ.__init__(self, segment)


class Leaf(Organ):
    def __init__(self, segment):
        Organ.__init__(self, segment)

    def is_too_short(self):
        if len(self.segments) == 1:
            if len(self.segments[0].points) == 2:
                return True
        return False


# ========================================================================
#       Code


def compute_orientation(vector_1, vector_2):
    angle = math.atan2(
        numpy.linalg.norm(numpy.cross(vector_1, vector_2)),
        numpy.dot(vector_1, vector_2))

    angle = angle * 180.0 / numpy.pi

    return angle


def segment_3d(vectors):
    segments = list()

    while vectors:
        vector = vectors.pop()
        my_seg = Segment(vector)

        while my_seg.find_segment(vectors, segments):
            continue

        segments.append(my_seg)

    return segments


def build_stem(segments):
    print "Number of segments : ", len(segments)

    # for segment in segments:
    #     angle_orientation = segment.get_angle_orientation()
    #     print "ANGLE : ", angle_orientation
    #     if 0 <= angle_orientation <= 45:
    #             list_of_possible_segment.append(segment)

    list_list = list()
    for segment_1 in segments[:]:

        list_candidate = list()
        list_candidate.append(segment_1)

        vector_1 = segment_1.get_vector()
        for segment_2 in segments[:]:
            if segment_1 is not segment_2:
                vector_2 = segment_2.get_vector()
                angle = compute_orientation(vector_1, vector_2)

                if angle <= 30:
                    list_candidate.append(segment_2)

        list_list.append(list_candidate)

    stems = list()
    for list_candidate in list_list:

        list_of_possible_segment = list_candidate

        while list_of_possible_segment:

            segment = list_of_possible_segment.pop()
            stem = Stem(segment)

            stop = False
            while stop is False:
                stop = True

                for seg_left in list_of_possible_segment[:]:
                    if stem.is_close(seg_left):
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

    for segment in segments[:]:
        if stem_choose.is_in(segment):
            segments.remove(segment)

    return stem_choose, segments


def build_leaf(segments, stem):
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

            my_leaf = Leaf(seg)

            stop = False
            while stop is False:
                stop = True
                for seg_left in segments[:]:
                    if not stem.is_close(seg_left):
                        if my_leaf.is_close(seg_left):
                            my_leaf.segments.append(seg_left)
                            segments.remove(seg_left)
                            stop = False

            leaves.append(my_leaf)

    for leaf in leaves[:]:
        if leaf.is_too_short():
            leaves.remove(leaf)

    # print "Number of leaf : ", len(leaves)

    return leaves, segments


def segment_organs_from_skeleton_3d(skeleton_3d):
    segments = segment_3d(skeleton_3d)

    stem, segments = build_stem(segments)

    leaves, segments = build_leaf(segments, stem)

    return stem, leaves, segments


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
