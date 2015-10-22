# -*- python -*-
#
#       calibration_tools.py :
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
import numpy
import pylab
import mpl_toolkits.mplot3d.axes3d
import scipy.optimize

#       ========================================================================
#       Local Import 
import transformations as tf

#       ========================================================================
#       Code


def compute_rotation_vectors(rotation_vectors, angles):

    def extrapolation_rotation_vector(angle, res):
        step = 60
        xyz = [[res[0]], [res[1]], [res[2]]]
        rxyz = [[res[3]], [res[4]], [res[5]]]

        rvec_src = rotation_vectors[angle - step]
        new_rvec = compute_rotation_vector(rvec_src, xyz, rxyz)

        # for i in range(1, 10):
        #     new_rvec = compute_rotation_vector(new_rvec, xyz, rxyz)

        # rotation_vectors[angle] = new_rvec

        return new_rvec

    def compute_rotation_vector(rvec_src, xyz, rxyz):

        matrix = tf.euler_matrix(rxyz[0][0],
                                 rxyz[1][0],
                                 rxyz[2][0],
                                 axes='sxyz')
        matrix = matrix[:3, :3]

        rvec = rvec_src.copy()
        rvec = numpy.dot(matrix, rvec)
        rvec = numpy.add(xyz, rvec)

        return rvec

    def minimize_function(x0):
        xyz = [[x0[0]], [x0[1]], [x0[2]]]
        rxyz = [[x0[3]], [x0[4]], [x0[5]]]

        distance = 0
        step = 60
        for angle in rotation_vectors:
            if angle + step not in rotation_vectors:
                continue
            if angle == 6:
                continue
            if angle == 3:
                continue

            rvec_src = rotation_vectors[angle]
            rvec_dest = rotation_vectors[angle + step]

            rvec = compute_rotation_vector(rvec_src, xyz, rxyz)

            distance += numpy.linalg.norm(rvec - rvec_dest)

        print distance * 100
        return distance * 100

    pi2 = 2 * numpy.pi
    bounds = [(-pi2, pi2), (-pi2, pi2), (-pi2, pi2),
              (-pi2, pi2), (-pi2, pi2), (-pi2, pi2)]

    optimize_result = scipy.optimize.differential_evolution(
        minimize_function, bounds)

    while minimize_function(optimize_result.x) > 5:
        optimize_result = scipy.optimize.differential_evolution(
            minimize_function, bounds)

    print optimize_result.x
    res = optimize_result.x

    for angle in angles:
        if angle not in rotation_vectors:
            rotation_vectors[angle] = extrapolation_rotation_vector(angle, res)

    return rotation_vectors


def compute_translation_vectors(translation_vectors, angles):

    def extrapolation_vector(angle, xyz, rxyz):
        tvec_src = translation_vectors[105]

        nb = int((angle - 105) / 3.0)

        tvec = compute_translation_vector(tvec_src, xyz, rxyz)

        for i in range(1, nb):
            tvec = compute_translation_vector(tvec, xyz, rxyz)

        translation_vectors[angle] = tvec

        return tvec

    def inv_extrapolation_vector(angle, xyz, rxyz):

        tvec_src = translation_vectors[0]

        nb = int((360 - angle) / 3.0)

        tvec = inv_compute_translation_vector(tvec_src, xyz, rxyz)

        for i in range(1, nb):
            tvec = inv_compute_translation_vector(tvec, xyz, rxyz)

        translation_vectors[angle] = tvec

        return tvec

    def inv_compute_translation_vector(tvec_src, xyz, rxyz):

        matrix = tf.euler_matrix(0,
                                 rxyz[1][0],
                                 rxyz[2][0],
                                 axes='sxyz')
        matrix = matrix[:3, :3]
        matrix = numpy.linalg.inv(matrix)

        tvec = tvec_src.copy()
        tvec = numpy.subtract(tvec, xyz)
        tvec = numpy.dot(matrix, tvec)

        return tvec

    def compute_translation_vector(tvec_src, xyz, rxyz):

        matrix = tf.euler_matrix(0,
                                 rxyz[1][0],
                                 rxyz[2][0],
                                 axes='sxyz')
        matrix = matrix[:3, :3]

        tvec = tvec_src.copy()
        tvec = numpy.dot(matrix, tvec)
        tvec = numpy.add(xyz, tvec)

        return tvec

    def minimize_function(x0):
        xyz = [[x0[0]], [x0[1]], [x0[2]]]
        rxyz = [[x0[3]], [x0[4]], [x0[5]]]

        distance = 0
        step = 3
        for angle in translation_vectors.keys():
            if angle + step not in translation_vectors:
                continue

            if angle == 3:
                continue
            if angle == 6:
                continue
            tvec_src = translation_vectors[angle]
            tvec_dest = translation_vectors[angle + step]

            tvec = compute_translation_vector(tvec_src,
                                              xyz,
                                              rxyz)

            distance += numpy.linalg.norm(tvec - tvec_dest)

        tvec_src = translation_vectors[105]
        tvec_dest = translation_vectors[0]

        tvec = compute_translation_vector(tvec_src, xyz, rxyz)

        for i in range(1, 85):
            tvec = compute_translation_vector(tvec, xyz, rxyz)

        distance += numpy.linalg.norm(tvec - tvec_dest)

        print distance
        return distance

    pi2 = 2 * numpy.pi
    r = 500
    bounds = [(-r, r), (-r, r), (-r, r),
              (-pi2, pi2), (-pi2, pi2), (-pi2, pi2)]

    optimize_result = scipy.optimize.differential_evolution(
        minimize_function, bounds)

    while minimize_function(optimize_result.x) > 25:
        optimize_result = scipy.optimize.differential_evolution(
            minimize_function, bounds)

    print optimize_result.x
    res = optimize_result.x

    xyz = [[res[0]], [res[1]], [res[2]]]
    rxyz = [[res[3]], [res[4]], [res[5]]]

    for angle in angles:
        if angle not in translation_vectors:
            if angle < 240:
                translation_vectors[angle] = extrapolation_vector(angle,
                                                                  xyz,
                                                                  rxyz)
            else:
                translation_vectors[angle] = inv_extrapolation_vector(angle,
                                                                      xyz,
                                                                      rxyz)

    return translation_vectors


def plot_vectors(vectors):
    fig = pylab.figure()
    ax = mpl_toolkits.mplot3d.axes3d.Axes3D(fig)

    for angle in vectors.keys():
        if vectors[angle] is not None:
            vector = vectors[angle]
            ax.scatter3D(vector[0][0], vector[1][0], vector[2][0])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    pylab.show()
