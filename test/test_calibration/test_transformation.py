import math
import random

import numpy

import openalea.phenomenal.calibration.transformations as tr


def test_reflection_matrix():
    v0 = numpy.random.random(4) - 0.5
    v0[3] = 1.
    v1 = numpy.random.random(3) - 0.5
    R = tr.reflection_matrix(v0, v1)
    numpy.allclose(2, numpy.trace(R))
    numpy.allclose(v0, numpy.dot(R, v0))
    v2 = v0.copy()
    v2[:3] += v1
    v3 = v0.copy()
    v2[:3] -= v1
    numpy.allclose(v2, numpy.dot(R, v3))


def test_reflection_from_matrix():
    v0 = numpy.random.random(3) - 0.5
    v1 = numpy.random.random(3) - 0.5
    M0 = tr.reflection_matrix(v0, v1)
    point, normal = tr.reflection_from_matrix(M0)
    M1 = tr.reflection_matrix(point, normal)
    tr.is_same_transform(M0, M1)


def test_rotation_matrix():
    R = tr.rotation_matrix(math.pi / 2, [0, 0, 1], [1, 0, 0])
    numpy.allclose(numpy.dot(R, [0, 0, 0, 1]), [1, -1, 0, 1])

    angle = (random.random() - 0.5) * (2 * math.pi)
    direc = numpy.random.random(3) - 0.5
    point = numpy.random.random(3) - 0.5
    R0 = tr.rotation_matrix(angle, direc, point)
    R1 = tr.rotation_matrix(angle - 2 * math.pi, direc, point)
    tr.is_same_transform(R0, R1)

    R0 = tr.rotation_matrix(angle, direc, point)
    R1 = tr.rotation_matrix(-angle, -direc, point)
    tr.is_same_transform(R0, R1)

    I = numpy.identity(4, numpy.float64)
    numpy.allclose(I, tr.rotation_matrix(math.pi * 2, direc))
    numpy.allclose(2,
                   numpy.trace(tr.rotation_matrix(math.pi / 2, direc, point)))


def test_projection_matrix():
    P = tr.projection_matrix([0, 0, 0], [1, 0, 0])
    numpy.allclose(P[1:, 1:], numpy.identity(4)[1:, 1:])

    point = numpy.random.random(3) - 0.5
    normal = numpy.random.random(3) - 0.5
    direct = numpy.random.random(3) - 0.5
    persp = numpy.random.random(3) - 0.5
    P0 = tr.projection_matrix(point, normal)
    P1 = tr.projection_matrix(point, normal, direction=direct)
    P2 = tr.projection_matrix(point, normal, perspective=persp)
    P3 = tr.projection_matrix(point, normal, perspective=persp, pseudo=True)
    tr.is_same_transform(P2, numpy.dot(P0, P3))

    P = tr.projection_matrix([3, 0, 0], [1, 1, 0], [1, 0, 0])
    v0 = (numpy.random.rand(4, 5) - 0.5) * 20
    v0[3] = 1
    v1 = numpy.dot(P, v0)
    numpy.allclose(v1[1], v0[1])

    numpy.allclose(v1[0], 3 - v1[1])


def test_shear_matrix():
    angle = (random.random() - 0.5) * 4 * math.pi
    direct = numpy.random.random(3) - 0.5
    point = numpy.random.random(3) - 0.5
    normal = numpy.cross(direct, numpy.random.random(3))
    S = tr.shear_matrix(angle, direct, point, normal)
    numpy.allclose(1, numpy.linalg.det(S))


def test_decompose_matrix():
    T0 = tr.translation_matrix([1, 2, 3])
    scale, shear, angles, trans, persp = tr.decompose_matrix(T0)
    T1 = tr.translation_matrix(trans)
    numpy.allclose(T0, T1)

    S = tr.scale_matrix(0.123)
    scale, shear, angles, trans, persp = tr.decompose_matrix(S)

    R0 = tr.euler_matrix(1, 2, 3)
    scale, shear, angles, trans, persp = tr.decompose_matrix(R0)
    R1 = tr.euler_matrix(*angles)
    numpy.allclose(R0, R1)


def test_compose_matrix():
    scale = numpy.random.random(3) - 0.5
    shear = numpy.random.random(3) - 0.5
    angles = (numpy.random.random(3) - 0.5) * (2 * math.pi)
    trans = numpy.random.random(3) - 0.5
    persp = numpy.random.random(4) - 0.5
    M0 = tr.compose_matrix(scale, shear, angles, trans, persp)
    result = tr.decompose_matrix(M0)
    M1 = tr.compose_matrix(*result)
    tr.is_same_transform(M0, M1)


def test_orthogonalization_matrix():
    O = tr.orthogonalization_matrix([10, 10, 10], [90, 90, 90])
    numpy.allclose(O[:3, :3], numpy.identity(3, float) * 10)

    O = tr.orthogonalization_matrix([9.8, 12.0, 15.5], [87.2, 80.7, 69.7])
    numpy.allclose(numpy.sum(O), 43.063229)


def test_affine_matrix_from_points():
    v0 = [[0, 1031, 1031, 0], [0, 0, 1600, 1600]]
    v1 = [[675, 826, 826, 677], [55, 52, 281, 277]]
    tr.affine_matrix_from_points(v0, v1)
    T = tr.translation_matrix(numpy.random.random(3) - 0.5)
    R = tr.random_rotation_matrix(numpy.random.random(3))
    S = tr.scale_matrix(random.random())
    M = tr.concatenate_matrices(T, R, S)
    v0 = (numpy.random.rand(4, 100) - 0.5) * 20
    v0[3] = 1
    v1 = numpy.dot(M, v0)
    v0[:3] += numpy.random.normal(0, 1e-8, 300).reshape(3, -1)
    M = tr.affine_matrix_from_points(v0[:3], v1[:3])
    numpy.allclose(v1, numpy.dot(M, v0))


def test_euler_from_quaternion():
    angles = tr.euler_from_quaternion([0.99810947, 0.06146124, 0, 0])
    numpy.allclose(angles, [0.123, 0, 0])


def test_quaternion_from_euler():
    q = tr.quaternion_from_euler(1, 2, 3, 'ryxz')
    numpy.allclose(q, [0.435953, 0.310622, -0.718287, 0.444435])


def test_quaternion_about_axis():
    q = tr.quaternion_about_axis(0.123, [1, 0, 0])
    numpy.allclose(q, [0.99810947, 0.06146124, 0, 0])


def test_quaternion_matrix():
    M = tr.quaternion_matrix([0.99810947, 0.06146124, 0, 0])
    numpy.allclose(M, tr.rotation_matrix(0.123, [1, 0, 0]))

    M = tr.quaternion_matrix([1, 0, 0, 0])
    numpy.allclose(M, numpy.identity(4))

    M = tr.quaternion_matrix([0, 1, 0, 0])
    numpy.allclose(M, numpy.diag([1, -1, -1, 1]))
