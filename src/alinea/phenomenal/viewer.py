# -*- python -*-
#
#       viewer.py :
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
import cv2
import numpy
import random

import mayavi.mlab
import matplotlib.cm
import matplotlib.pyplot


#       ========================================================================
#       Show reconstruction 3d


def show_points_3d(points_3d,
                   color=None,
                   scale_factor=5.0,
                   figure_name="Cubes"):
    mayavi.mlab.figure(figure_name)

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    plot_points_3d(points_3d, color=color, scale_factor=scale_factor)

    mayavi.mlab.show()


def plot_points_3d(points_3d, color=None, scale_factor=5):

    pts = numpy.array(points_3d)
    pts = pts.astype(int)

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    if len(points_3d) > 0:
        mayavi.mlab.points3d(pts[:, 0], pts[:, 1], pts[:, 2],
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
                names_axes=None):

    matplotlib.pyplot.title(name_windows)
    number_of_images = len(images)

    i = 1
    for image in images:
        ax = matplotlib.pyplot.subplot(1, number_of_images, i)

        if names_axes is None:
            ax.set_title('Image %d/%d' % (i, number_of_images))
        else:
            ax.set_title(names_axes[i])

        if len(numpy.shape(image)) == 2:
            img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            ax.imshow(img)
        else:
            img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            ax.imshow(img)

        i += 1

    matplotlib.pyplot.show()


def show_image(image, name_windows='Image'):

    matplotlib.pyplot.title(name_windows)

    if len(numpy.shape(image)) == 2:
        img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        matplotlib.pyplot.imshow(img)
    else:
        img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        matplotlib.pyplot.imshow(img)

    matplotlib.pyplot.show()


def show_mesh(vertices, faces, normals=None, centers=None):

    if normals is not None and centers is not None:
        mayavi.mlab.quiver3d(centers[:, 0], centers[:, 1], centers[:, 2],
                             normals[:, 0], normals[:, 1], normals[:, 2],
                             line_width=1.0, scale_factor=1)

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    mayavi.mlab.triangular_mesh([vert[0] for vert in vertices],
                                [vert[1] for vert in vertices],
                                [vert[2] for vert in vertices],
                                faces)

    mayavi.mlab.show()


def show_image_with_chessboard_corners(image,
                                       corners,
                                       name_windows="Chessboard corners"):
    img = image.copy()

    corners = corners.astype(int)
    img[corners[:, 0, 1], corners[:, 0, 0]] = [0, 0, 255]

    matplotlib.pyplot.title(name_windows)
    matplotlib.pyplot.imshow(img)
    matplotlib.pyplot.show()


def show_chessboard_3d_projection_on_image(image,
                                           angle,
                                           chessboard,
                                           chessboard_params,
                                           projection,
                                           name_windows="Chessboard corners"):
    img = image.copy()

    # Plot Corners detect by OpenCv
    corners = chessboard.corners_points[angle]
    corners = corners.astype(int)
    img[corners[:, 0, 1], corners[:, 0, 0]] = [0, 0, 255]

    # Plot projection of position conners of chessboard 3d
    chessboard_pts = chessboard.global_corners_position_3d(
        *chessboard_params.get_parameters())

    corners = [projection.project_point(pt, angle) for pt in chessboard_pts]
    for corner in corners:
        x, y = corner
        img[int(y), int(x)] = [255, 0, 0]

    # Show image
    matplotlib.pyplot.title(name_windows)
    matplotlib.pyplot.imshow(img)
    matplotlib.pyplot.show()
