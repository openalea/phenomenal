# -*- python -*-
#
#       example_stack_image.py :
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
import time
import collections
import cv2
import numpy
import scipy.optimize

#       ========================================================================
#       Local Import
import alinea.phenomenal.result_viewer
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
import alinea.phenomenal.skeletonize_3d


#       ========================================================================
#       Code


def run_example(data_directory, calibration_name):

    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            images_selected = dict()
            for angle in images:
                if 0 <= angle <= 360:
                    images_selected[angle] = images[angle]

            calibration = alinea.phenomenal.calibration_model.\
                Calibration.read_calibration(
                    calibration_name, file_is_in_share_directory=False)

            points_3d = alinea.phenomenal.multi_view_reconstruction.\
                reconstruction_3d(images_selected,
                                  calibration,
                                  precision=2,
                                  verbose=True)

            matrix = alinea.phenomenal.data_transformation.points_3d_to_matrix(
                points_3d, 2)

            alinea.phenomenal.data_transformation.save_matrix_like_stack_image(
                matrix,
                data_directory + 'stack_image_' + pot_id + '_' + date + '/')


def run_example_2(data_directory, calibration_name):

    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            images_selected = dict()
            for angle in images:
                if 0 <= angle <= 360:
                    images_selected[angle] = images[angle]

            calibration = alinea.phenomenal.calibration_model.\
                Calibration.read_calibration(
                    calibration_name, file_is_in_share_directory=False)

            points_3d = alinea.phenomenal.multi_view_reconstruction.\
                reconstruction_3d(images_selected,
                                  calibration,
                                  precision=2,
                                  verbose=True)

            alinea.phenomenal.result_viewer.show_points_3d(
                points_3d, scale_factor=1)

            t0 = time.time()
            matrix, index = alinea.phenomenal.data_transformation.\
                points_3d_to_matrix(points_3d, 2)

            index_new = collections.deque()
            mat = matrix.copy()
            while True:
                try:
                    x, y, z = index.popleft()

                    if (matrix[x - 1, y - 1, z] == 1 and
                        matrix[x - 1, y, z] == 1 and
                        matrix[x - 1, y + 1, z] == 1 and
                        matrix[x, y - 1, z] == 1 and
                        matrix[x, y + 1, z] == 1 and
                        matrix[x + 1, y - 1, z] == 1 and
                        matrix[x + 1, y, z] == 1 and
                        matrix[x + 1, y + 1, z] == 1 and

                        matrix[x - 1, y - 1, z - 1] == 1 and
                        matrix[x - 1, y, z - 1] == 1 and
                        matrix[x - 1, y + 1, z - 1] == 1 and
                        matrix[x, y - 1, z - 1] == 1 and
                        matrix[x, y, z - 1] == 1 and
                        matrix[x, y + 1, z - 1] == 1 and
                        matrix[x + 1, y - 1, z - 1] == 1 and
                        matrix[x + 1, y, z - 1] == 1 and
                        matrix[x + 1, y + 1, z - 1] == 1 and

                        matrix[x - 1, y - 1, z + 1] == 1 and
                        matrix[x - 1, y, z + 1] == 1 and
                        matrix[x - 1, y + 1, z + 1] == 1 and
                        matrix[x, y - 1, z + 1] == 1 and
                        matrix[x, y, z + 1] == 1 and
                        matrix[x, y + 1, z + 1] == 1 and
                        matrix[x + 1, y - 1, z + 1] == 1 and
                        matrix[x + 1, y, z + 1] == 1 and
                            matrix[x + 1, y + 1, z + 1] == 1):
                        mat[x, y, z] = 0
                    else:
                        index_new.append((x, y, z))

                except IndexError:

                    if len(index) > 0:
                        index_new.append((x, y, z))
                        continue
                    else:
                        break

            t1 = time.time()
            print 'TOTAL !! ',  t1 - t0

            t0 = time.time()

            index = index_new
            index_new = collections.deque()

            ball_size = 20
            x_size, y_size, z_size = numpy.shape(mat)

            def func_lsq(p, x, y, z):
                return z + (p[0] * x + p[1] * y + p[2])

            p = [numpy.random.random() * 10.0,
                 numpy.random.random() * 10.0,
                 numpy.random.random() * 10.0]

            normal = list()
            print len(index)
            while True:
                try:
                    x, y, z = index.popleft()
                    index_new.append((x, y, z))

                    x_min = max(x - ball_size, 0)
                    y_min = max(y - ball_size, 0)
                    z_min = max(z - ball_size, 0)

                    x_max = min(x + ball_size, x_size)
                    y_max = min(y + ball_size, y_size)
                    z_max = min(z + ball_size, z_size)

                    m = matrix[x_min:x_max, y_min:y_max, z_min:z_max]

                    xx, yy, zz = numpy.where(m == 1)

                    if len(xx) > 3:
                        result = scipy.optimize.leastsq(
                            func_lsq, p, args=(xx, yy, zz))

                        a, b, d = result[0]
                        normal.append((a, b, d))

                        # print a, b, 1.0, d

                except IndexError:
                    break

            t1 = time.time()
            print 'TOTAL !! ',  t1 - t0

            points_3d = alinea.phenomenal.data_transformation.\
                matrix_to_points_3d(mat, 2, [0, 0, 0])

            alinea.phenomenal.result_viewer.show_points_3d(
                points_3d, scale_factor=1.0)

            alinea.phenomenal.misc.write_xyz(
                points_3d, 'test_mesh')


            # skeleton_3d = alinea.phenomenal.skeletonize_3d.\
            #     skeletonize_3d_segment(points_3d, 10, 50)
            #
            # mayavi.mlab.figure("Skeleton")
            # alinea.phenomenal.result_viewer.plot_vectors(skeleton_3d)
            # # alinea.phenomenal.result_viewer.plot_points_3d(
            # #     points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
            # mayavi.mlab.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example_2('../../local/data_set_0962_A310_ARCH2013-05-13/',
                  '../calibration/fitted_result')
