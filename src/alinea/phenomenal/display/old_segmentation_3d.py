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
import random
import mayavi.mlab
# ==============================================================================


def plot_vectors(vectors, color=None, tube_radius=5.0):
    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    for point_1, point_2, _ in vectors:
        mayavi.mlab.plot3d([point_1[0], point_2[0]],
                           [point_1[1], point_2[1]],
                           [point_1[2], point_2[2]],
                           color=color,
                           tube_radius=tube_radius)

    return color


def plot_segments(segments,
                  color=None,
                  tube_radius=8.0,
                  color_each_segment=False):
    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    for segment in segments:
        x = list()
        y = list()
        z = list()

        if color_each_segment is True:
            color = (random.uniform(0, 1),
                     random.uniform(0, 1),
                     random.uniform(0, 1))

        for point in segment.points:
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])

        mayavi.mlab.plot3d(x, y, z,
                           color=color,
                           tube_radius=tube_radius)

    return color