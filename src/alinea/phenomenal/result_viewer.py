# -*- python -*-
#
#       tools_test.py :
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

import random
import mayavi.mlab
# import matplotlib.pylab
import matplotlib.cm
import pylab


#       ========================================================================
#       Show reconstruction 3d


def show_points_3d(points_3d,
                   color=None,
                   scale_factor=10.0,
                   figure_name="Cubes"):
    mayavi.mlab.figure(figure_name)

    plot_points_3d(points_3d, color=color, scale_factor=scale_factor)

    mayavi.mlab.show()
    mayavi.mlab.clf()
    mayavi.mlab.close()


def plot_points_3d(points_3d, color=None, scale_factor=5):
    x = list()
    y = list()
    z = list()

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    for point_3d in points_3d:

        print point_3d

        x.append(int(round(point_3d[0])))
        y.append(int(round(point_3d[1])))
        z.append(int(round(point_3d[2])))

    if len(point_3d) > 0:
        mayavi.mlab.points3d(x, y, z,
                             mode='cube',
                             color=color,
                             scale_factor=scale_factor)

    return color


def plot_vectors(vectors, color=None, tube_radius=8.0):
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

#       ========================================================================


def show_images(images,
                name_windows='Image Comparison',
                names_axes=None,
                color_map_axes=None):

    fig = pylab.figure()
    fig.canvas.set_window_title(name_windows)

    number_of_images = len(images)

    i = 1
    for image in images:
        ax = fig.add_subplot(1, number_of_images, i)

        if names_axes is None:
            ax.set_title('Image %d/%d' % (i, number_of_images))
        else:
            ax.set_title(names_axes[i])

        if color_map_axes is None:
            im = pylab.imshow(image)
        else:
            im = pylab.imshow(image, cmap=color_map_axes[i])

        i += 1

    pylab.show()

    fig.clear()
    pylab.close(fig)



def show_image(image,
               name_windows='Image',
               color_map=matplotlib.pylab.gray()):

    fig = matplotlib.pylab.figure()
    fig.canvas.set_window_title(name_windows)
    matplotlib.pylab.title(name_windows)
    matplotlib.pylab.imshow(image, cmap=color_map)

    matplotlib.pylab.show()

    fig.clf()
    matplotlib.pylab.close(fig)

