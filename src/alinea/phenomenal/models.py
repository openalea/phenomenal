# -*- python -*-
#
#       models.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
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

"""
Models for  estimation of biological traits from image analysis
"""

#       ========================================================================
#       External Import
import datetime
import numpy

#       ========================================================================


def strptime(dateseq, format='%Y-%m-%d'):
    """
    string -> date conversion
    """
    return map(lambda x: datetime.datetime.strptime(x, format), dateseq)


def plant_area(pixel_counts, a=3.261011e-06, b=0.04240879):
    """
    Plant area estimation from pixels counts
    """
    pix = numpy.array(pixel_counts)
    return a * pix + b


class StemModel(object):
        def __init__(self, first_point, last_point, radius):
            self.first_point = first_point
            self.last_point = last_point
            self.radius = 10

            self.length = np.linalg.norm(self.last_point - self.first_point)


        def compute_distance(self, x, y, z):

            dx = self.last_point[0] - self.first_point[0]
            dy = self.last_point[1] - self.first_point[1]
            dz = self.last_point[2] - self.first_point[2]

            pdx = x - self.first_point[0]
            pdy = y - self.first_point[1]
            pdz = z - self.first_point[2]

            dot = pdx * dx + pdy * dy + pdz * dz

            if dot < 0.0 or dot > self.length:
                return 0
            else:
                dsq = (pdx * pdx + pdy * pdy + pdz * pdz) - dot * dot / self.length

                if dsq > self.radius:
                    return 0
                else:
                    return 1

        def distance(self, cubes):
            global_distance = 0
            for cube in cubes:
                global_distance += self.compute_distance(cube.position[0, 0],
                                                         cube.position[0, 1],
                                                         cube.position[0, 2])

            return global_distance

        def distance_2(self, cubes):
            global_distance = 0
            for cube in cubes:

                pt = [cube.position[0, 0],
                      cube.position[0, 1],
                      cube.position[0, 2]]

                t_min = self.project_point_on_center_line(pt)

                if 0 < t_min < 1:

                    distance = self.distance_from_center_line(t_min, pt)

                    if distance < self.radius:
                        global_distance -= 1

                global_distance += 1

            return global_distance


        def project_point_on_center_line(self, pt):
            range = self.point_substract(self.first_point, self.last_point)

            return ((self.dot_product(pt, range)
                     - self.dot_product(self.last_point, range))
                    / self.dot_product(range, range))

        def distance_from_center_line(self, tmin, pt):

            linept = self.parametric_point_on_center_line(tmin)

            diff = self.point_substract(linept, pt)

            return np.sqrt(self.dot_product(diff, diff))

        def parametric_point_on_center_line(self, t):

            range = self.point_substract(self.first_point, self.last_point)

            return [self.last_point[0] + t * range[0],
                    self.last_point[1] + t * range[1],
                    self.last_point[2] + t * range[2]]

        def point_substract(self, a, b):
            return [a[0] - b[0],
                    a[1] - b[1],
                    a[2] - b[2]]

        def dot_product(self, a, b):
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]