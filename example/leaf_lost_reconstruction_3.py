# -*- python -*-
#
#       leaf_lost_reconstruction_3.py : 
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
# ==============================================================================
import multiprocessing
import gc
import math
import matplotlib.pyplot
import numpy

import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
# ==============================================================================


def show_image(image):
    im = image.copy()
    im = im.astype(numpy.uint8)

    fig = matplotlib.pyplot.figure(1)
    matplotlib.pyplot.imshow(im)
    matplotlib.pyplot.show()


def daemon_show_image(image):
    proc = multiprocessing.Process(target=show_image, args=(image,))
    proc.daemon = True
    proc.start()
    proc.join()


def create_points_3d_leaf(points_3d, projection, im, angle, verbose=False, ):
    res = alinea.phenomenal.data_transformation.limit_points_3d(points_3d)
    x_min, y_min, z_min, x_max, y_max, z_max = res

    if verbose:
        print 'Limits points 3D : ', x_min, y_min, z_min, x_max, y_max, z_max

    dict_point_3d_leaf = dict()
    images_selected = dict()
    images_selected[angle] = im

    for i in range(int(x_min), int(x_max), int(radius * 2.0)):
        print i
        dict_point_3d_leaf[
            i], err = alinea.phenomenal.multi_view_reconstruction. \
            reconstruction_3d(images_selected, projection, radius,
                              origin_point=(float(i), 0.0, 0.0))

    if verbose:
        import mayavi.mlab

        mayavi.mlab.figure('figure')

        mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

        for i in dict_point_3d_leaf:
            alinea.phenomenal.viewer.plot_points_3d(dict_point_3d_leaf[i])
        alinea.phenomenal.viewer.plot_points_3d(points_3d)
        mayavi.mlab.show()

    return dict_point_3d_leaf


def update_mat(mat, index):
    x_length, y_length, z_length = mat.shape

    def next_neighbort(x, y, z, value):
        l = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if mat[x + i, y + j, z + k] == value:
                        l.append((x + i, y + j, z + k))
        return l

    def have_neighbort(x, y, z):
        if (0 < x < x_length - 1 and
                        0 < y < y_length - 1 and
                        0 < z < z_length - 1):
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if mat[x + i, y, z + j] == 1:
                        return True
        return False

    for point_3d in index:
        value = mat[point_3d]
        if value > 1:
            if have_neighbort(*point_3d):
                mat[point_3d] = 1
                x, y, z = point_3d

                l = next_neighbort(x, y, z, value)

                while True:
                    try:
                        xx, yy, zz = l.pop()
                        if mat[xx, yy, zz] == value:
                            mat[xx, yy, zz] = 1
                            l += next_neighbort(xx, yy, zz, value)

                    except IndexError:
                        break
    return mat


if __name__ == '__main__':

    # ==========================================================================
    # Define parameters of reconstruction

    radius = 4
    verbose = True

    # ==========================================================================
    # Load images, camera parameters and create projection object

    # Load images binarize
    images = alinea.phenomenal.data_load.test_plant_1_images_binarize()

    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.data_load.\
        test_plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    # ==========================================================================
    # Load Point_3D of the reference plant

    points_3d_path = alinea.phenomenal.data_load.test_plant_1_points_3d_path(
        radius=radius)

    images_selected = dict()
    for angle in range(0, 360, 30):
        images_selected[angle] = images[angle]

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d_2(
        images_selected, projection, radius, verbose=True)

    if verbose:
        alinea.phenomenal.viewer.show_points_3d(points_3d)

    # ==========================================================================
    # Compute limits points of points_3d reference plant

    res = alinea.phenomenal.data_transformation.limit_points_3d(points_3d)
    x_min, y_min, z_min, x_max, y_max, z_max = res

    if verbose:
        print 'Limits points 3D : ', x_min, y_min, z_min, x_max, y_max, z_max

    # ==========================================================================
    # Compute shape image

    shape_image = images[0].shape
    height_image, length_image = shape_image

    # ==========================================================================
    # Compute IMAGE leaf not reconstruct

    image_leaf = dict()
    for angle in range(0, 360, 30):
        # Build image projection of points_3d cloud
        img = alinea.phenomenal.multi_view_reconstruction. \
            project_points_on_image(points_3d,
                                    radius,
                                    shape_image,
                                    projection,
                                    angle)

        image_leaf[angle] = numpy.subtract(images[angle], img)
        image_leaf[angle][image_leaf[angle] == -255] = 0

        print "Angle : ", angle, ' Err : ', numpy.count_nonzero(
            image_leaf[angle])

    # ==========================================================================
    # Define angle of reference

    angle_ref = 90

    # ==========================================================================
    # Reconstruct leaf of angle_ref image

    import collections

    points_3d_origin = collections.deque()
    for i in range(int(x_min), int(x_max), int(radius * 2.0)):
        points_3d_origin.append((float(i), 0.0, 0.0))

    images_selected = dict()
    images_selected[angle_ref] = image_leaf[angle_ref]
    print radius
    points_3d_leaf = alinea.phenomenal.multi_view_reconstruction. \
        reconstruction_3d(images_selected,
                          projection,
                          radius,
                          points_3d=points_3d_origin,
                          verbose=True)

    # Valid if the projection on image and image angle ref is 0
    img = alinea.phenomenal.multi_view_reconstruction. \
        project_points_on_image(
            points_3d_leaf,
            radius,
            shape_image,
            projection,
            angle_ref)

    img = numpy.subtract(image_leaf[angle_ref], img)
    img[img == -255] = 0

    print 'VALIDATION - error reconstruction : ', numpy.count_nonzero(img)

    if verbose:
        import mayavi.mlab

        mayavi.mlab.figure('figure')

        mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

        alinea.phenomenal.viewer.plot_points_3d(points_3d_leaf)
        alinea.phenomenal.viewer.plot_points_3d(points_3d)
        mayavi.mlab.show()

    # ==========================================================================
    # ==========================================================================

    where_x_y = dict()
    for angle in xrange(0, 360, 30):
        where_x_y[angle] = numpy.where(images[angle] > 0)

    def distance_closest_point(angle, pt_x, pt_y):
        xx, yy = where_x_y[angle]

        return min((xx - pt_x) ** 2 + (yy - pt_y) ** 2)

    # ==========================================================================
    # ==========================================================================

    index = numpy.where(image_leaf[angle_ref] > 0)

    print len(index[0])
    groups = dict()
    for i in xrange(len(index[0])):
        x, y = (index[0][i], index[1][i])
        groups[x, y] = list()

    print 'Length leaf voxel', len(points_3d_leaf)
    inf = float('inf')
    for pt in points_3d_leaf:

        # ======================================================================
        sum_dist = 0
        for angle in xrange(0, 360, 30):

            b = alinea.phenomenal.multi_view_reconstruction.\
                point_3d_is_in_image(images[angle],
                                     height_image, length_image,
                                     pt, projection, angle, radius)

            if b:
                sum_dist += 1

            # pt_x, pt_y = projection.project_point(pt, angle)
            #
            # if pt_x < 0 or pt_x > length_image:
            #     sum_dist = inf
            #     break
            #
            # if pt_y < 0 or pt_y > height_image:
            #     sum_dist = inf
            #     break
            #
            # sum_dist += distance_closest_point(angle, int(pt_x), int(pt_y))

        # ======================================================================

        res = alinea.phenomenal.multi_view_reconstruction.bbox_projection(
            pt, radius, projection, angle_ref)

        x_min, x_max, y_min, y_max = res

        x_min = min(max(math.floor(x_min), 0), length_image - 1)
        x_max = min(max(math.ceil(x_max), 0), length_image - 1)
        y_min = min(max(math.floor(y_min), 0), height_image - 1)
        y_max = min(max(math.ceil(y_max), 0), height_image - 1)

        pts = image_leaf[angle_ref][y_min:y_max + 1, x_min:x_max + 1]
        index = numpy.where(pts > 0)

        for i in xrange(len(index[0])):
            x, y = (index[0][i] + y_min, index[1][i] + x_min)
            groups[(x, y)].append((pt, sum_dist))

    print 'Number of points : ', len(points_3d_leaf)
    print 'Length groups : ', len(groups.keys())

    # ==========================================================================

    import time
    start_time = time.time()

    # ==========================================================================
    inf = float('inf')
    mypt3d = list()
    for pt2d in groups:
        min_dist = 0
        save_pt = None
        for pt3D, sum_dist in groups[pt2d]:
            if sum_dist > min_dist:
                min_dist = sum_dist
                save_pt = pt3D
        if save_pt is not None:
            mypt3d.append(save_pt)
    # ==========================================================================

    print 'DONE - Time : ', time.time() - start_time

    # ==========================================================================

    del groups
    gc.collect()

    print 'DONE - result : ', len(mypt3d)
    print shape_image

    img = alinea.phenomenal.multi_view_reconstruction. \
        project_points_on_image(
        mypt3d, radius, shape_image, projection, angle_ref)

    img = numpy.subtract(image_leaf[angle_ref], img)
    img[img == -255] = 0

    print 'VALIDATION - error reconstruction : ', numpy.count_nonzero(img)

    if verbose:
        import mayavi.mlab

        mayavi.mlab.figure('figure')

        mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
        mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

        alinea.phenomenal.viewer.plot_points_3d(mypt3d)
        alinea.phenomenal.viewer.plot_points_3d(points_3d)
        mayavi.mlab.show()

    # ==========================================================================