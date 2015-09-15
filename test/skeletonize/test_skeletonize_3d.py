# -*- python -*-
#
#       test_skeletonize_3d.py :
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
import glob
import cv2
import numpy as np
from mayavi import mlab
import re

#       ========================================================================
#       Local Import
import alinea.phenomenal.skeletonize_3d as skeletonize_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.segmentation_3d as segmentation_3d
import phenomenal.test.tools_test as tools_test
#       ========================================================================
#       Code

def read_xyz(directory='./'):

    xyz_files = glob.glob(directory + '*.xyz')

    for i in range(len(xyz_files)):

        read_cubes = list()
        with open(xyz_files[i], 'r') as f:

            radius = float(f.readline())
            for line in f:
                position = re.findall(r'[-0-9.]+', line)
                cube = reconstruction_3d.algo.Cube(position[0],
                                                   position[1],
                                                   position[2],
                                                   radius)

                read_cubes.append(cube)

        f.close()

        tools_test.show_cubes(read_cubes, figure_name=xyz_files[i])

        return read_cubes


def test_skeletonize_3d():
    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    # directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'
    #
    # files = glob.glob(directory + '*.png')
    #
    # angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)
    #
    # images = dict()
    # for i in range(len(files)):
    #     images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)
    #
    # #   ========================================================================
    #
    # opencv_calibration = calibration_chessboard.Calibration.read_calibration(
    #     'calibration')
    #
    # image_0_240 = dict()
    # for angle in images:
    #     if angle <= 240:
    #         image_0_240[angle] = images[angle]
    #
    # cubes = reconstruction_3d.reconstruction_3d(
    #     image_0_240, opencv_calibration, 5)


    #   ========================================================================

    cubes = read_xyz()
    cubes = convert_orientation_cubes(cubes)

    # class my_stem_model(object):
    #     def __init__(self, first_point, last_point, radius):
    #         self.first_point = first_point
    #         self.last_point = last_point
    #         self.radius = 10
    #
    #         self.length = np.linalg.norm(self.last_point - self.first_point)
    #
    #
    #     def compute_distance(self, x, y, z):
    #
    #         dx = self.last_point[0] - self.first_point[0]
    #         dy = self.last_point[1] - self.first_point[1]
    #         dz = self.last_point[2] - self.first_point[2]
    #
    #         pdx = x - self.first_point[0]
    #         pdy = y - self.first_point[1]
    #         pdz = z - self.first_point[2]
    #
    #         dot = pdx * dx + pdy * dy + pdz * dz
    #
    #         if dot < 0.0 or dot > self.length:
    #             return 0
    #         else:
    #             dsq = (pdx * pdx + pdy * pdy + pdz * pdz) - dot * dot / self.length
    #
    #             if dsq > self.radius:
    #                 return 0
    #             else:
    #                 return 1
    #
    #     def distance(self, cubes):
    #         global_distance = 0
    #         for cube in cubes:
    #             global_distance += self.compute_distance(cube.position[0, 0],
    #                                                      cube.position[0, 1],
    #                                                      cube.position[0, 2])
    #
    #         return global_distance
    #
    #     def distance_2(self, cubes):
    #         global_distance = 0
    #         for cube in cubes:
    #
    #             pt = [cube.position[0, 0],
    #                   cube.position[0, 1],
    #                   cube.position[0, 2]]
    #
    #             t_min = self.project_point_on_center_line(pt)
    #
    #             if 0 < t_min < 1:
    #
    #                 distance = self.distance_from_center_line(t_min, pt)
    #
    #                 if distance < self.radius:
    #                     global_distance -= 1
    #
    #             global_distance += 1
    #
    #         return global_distance
    #
    #
    #     def project_point_on_center_line(self, pt):
    #         range = self.point_substract(self.first_point, self.last_point)
    #
    #         return ((self.dot_product(pt, range)
    #                  - self.dot_product(self.last_point, range))
    #                 / self.dot_product(range, range))
    #
    #     def distance_from_center_line(self, tmin, pt):
    #
    #         linept = self.parametric_point_on_center_line(tmin)
    #
    #         diff = self.point_substract(linept, pt)
    #
    #         return np.sqrt(self.dot_product(diff, diff))
    #
    #     def parametric_point_on_center_line(self, t):
    #
    #         range = self.point_substract(self.first_point, self.last_point)
    #
    #         return [self.last_point[0] + t * range[0],
    #                 self.last_point[1] + t * range[1],
    #                 self.last_point[2] + t * range[2]]
    #
    #     def point_substract(self, a, b):
    #         return [a[0] - b[0],
    #                 a[1] - b[1],
    #                 a[2] - b[2]]
    #
    #     def dot_product(self, a, b):
    #         return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


    #   ========================================================================

    # mlab.figure("3D Reconstruction")
    # tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    #
    # x = cubes[1000].position[0, 0]
    # y = cubes[1000].position[0, 1]
    # z = cubes[1000].position[0, 2]

    # stem = my_stem_model(np.array([0, 0, 0]),
    #                      np.array([x, y, z]),
    #                      5)
    # print "GO"
    # print stem.distance_2(cubes)
    #
    # tools_test.plot_vectors([[stem.first_point, stem.last_point, None]],
    #                         tube_radius=stem.radius)
    # mlab.show()

    # from scipy import optimize
    #
    # def minimize_function(x0):
    #     point_1 = np.array([x0[0], x0[1], x0[2]])
    #     point_2 = np.array([x0[3], x0[4], x0[5]])
    #     radius = x0[6]
    #
    #     stem = my_stem_model(point_1, point_2, radius)
    #
    #     distance = stem.distance_2(cubes)
    #
    #     print distance
    #     return distance

    # print len(cubes)
    # print len(cubes) * len(cubes)
    #
    # return


    # save_stem = None
    # min_distance = 0
    # for cube_1 in cubes:
    #     for cube_2 in cubes:
    #
    #         x1 = cube_1.position[0, 0]
    #         y1 = cube_1.position[0, 1]
    #         z1 = cube_1.position[0, 2]
    #
    #         x2 = cube_2.position[0, 0]
    #         y2 = cube_2.position[0, 1]
    #         z2 = cube_2.position[0, 2]
    #
    #         point_1 = np.array([x1, y1, z1])
    #         point_2 = np.array([x2, y2, z2])
    #         radius = 10
    #
    #         stem = my_stem_model(point_1, point_2, radius)
    #
    #         distance = stem.distance_2(cubes)
    #
    #         print distance
    #
    #         if distance < min_distance:
    #             min_distance = distance
    #             save_stem = stem

    #
    # val = 250
    #
    # bounds = [(-val, val), (-val, val), (-val, val),
    #           (-val, val), (-val, val), (-val, val),
    #           (0, 10)]
    #
    #
    #
    # optimize_result = optimize.differential_evolution(minimize_function,
    #                                                   bounds)

    # print optimize_result
    # x0 = optimize_result.x
    #
    # point_1 = np.array([x0[0], x0[1], x0[2]])
    # point_2 = np.array([x0[3], x0[4], x0[5]])
    # radius = x0[6]
    #
    # stem = my_stem_model(point_1, point_2, radius)

    # stem = save_stem

    mlab.figure("3D Reconstruction")
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)

    #
    # tools_test.plot_vectors([[stem.first_point, stem.last_point, None]],
    #                         tube_radius=stem.radius)
    mlab.show()

    mlab.clf()
    mlab.close()


    #   ========================================================================

    # skeletonize.skeletonize_3d_transform_distance(opencv_cubes)

    # skeletonize_3d.test_skeletonize_3d(cubes, 10, 20)

    skeleton_3d = skeletonize_3d.skeletonize_3d_segment(cubes, 10, 50)




    #   ========================================================================

    mlab.figure("Skeleton")
    tools_test.plot_vectors(skeleton_3d)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    stem, leaves, segments = \
        segmentation_3d.segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mlab.figure("Organs")
    for leaf in leaves:
        tools_test.plot_segments(leaf.segments)
    tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    mlab.figure("Propagation")

    stem_cubes = give_cube(stem, cubes[0].radius)
    color = tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(stem_cubes, color=color, scale_factor=3)

    for leaf in leaves:
        leaf_cubes = give_cube(leaf, cubes[0].radius)
        color = tools_test.plot_segments(leaf.segments)
        tools_test.plot_cubes(leaf_cubes, color=color, scale_factor=3)

    # tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    from random import uniform
    #
    stem_cubes = convert_orientation_cubes(stem_cubes)
    #
    for angle in image_0_240:

        image = image_0_240[angle]

        for leaf in leaves:
            color = (int(uniform(0, 255)),
                     int(uniform(0, 255)),
                     int(uniform(0, 255)))

            leaf_cube = give_cube(leaf, cubes[0].radius)
            leaf_cube = convert_orientation_cubes(leaf_cube)

            image = reconstruction_3d.re_projection_cubes_to_image(
                leaf_cube,
                image,
                opencv_calibration[angle],
                color=color)

        color = (int(uniform(0, 255)),
                 int(uniform(0, 255)),
                 int(uniform(0, 255)))

        image = reconstruction_3d.re_projection_cubes_to_image(
            stem_cubes,
            image,
            opencv_calibration[angle],
            color=color)

        tools_test.show_image(image, str(angle))

    #   ========================================================================

    for angle in image_0_240:

        image = image_0_240[angle]

        for leaf in leaves:
            leaf_cube = give_cube(leaf, cubes[0].radius)
            leaf_cube = convert_orientation_cubes(leaf_cube)

            image = reconstruction_3d.re_projection_cubes_to_image(
                leaf_cube,
                image,
                opencv_calibration[angle],
                color=(0, 0, 0))

        image = reconstruction_3d.re_projection_cubes_to_image(
            stem_cubes,
            image,
            opencv_calibration[angle],
            color=(255, 255, 255))

        # tools_test.show_image(image, str(angle))

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image[image == 255] = 1

        import alinea.phenomenal.skeletonize_2d as skeletonize2d
        import alinea.phenomenal.segmentation_2d as segmentation_2d

        skeleton_1 = skeletonize2d.skeletonize_image_skimage(image)
        segmented = segmentation_2d.segment_organs_skeleton_image(skeleton_1)

        tools_test.show_image(image, str(angle))
        tools_test.show_image(skeleton_1, str(angle))
        tools_test.show_image(segmented, str(angle))

        # tools_test.show_comparison_3_image(image, skeleton_1, segmented)


def give_cube(organ, radius):
    cubes = list()

    for segment in organ.segments:
        for component in segment.component:
            for point in component:
                cube = reconstruction_3d.algo.Cube(point[0],
                                                   point[1],
                                                   point[2],
                                                   radius)

                cubes.append(cube)

    return cubes


def propagate_organs(cubes, organ):

    organ_cubes = list()
    new_cubes = list()

    print 'NB : ', len(organ.segments)
    # 7101

    i = 0
    for cube in cubes:
        ok = False
        for segment in organ.segments:
            for component in segment.component:
                for point in component:
                    if cube.position[0, 0] == point[0]:
                        if cube.position[0, 1] == point[1]:
                            if cube.position[0, 2] == point[2]:
                                organ_cubes.append(cube)
                                ok = True
        if ok is False:
            new_cubes.append(cube)

        print i
        i += 1

    return organ_cubes, new_cubes


def convert_orientation_cubes(cubes):

    for cube in cubes:
        x = cube.position[0, 0]
        y = - cube.position[0, 2]
        z = - cube.position[0, 1]

        cube.position[0, 0] = x
        cube.position[0, 1] = y
        cube.position[0, 2] = z

    return cubes


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_skeletonize_3d()
