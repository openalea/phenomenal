# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
A 3D 6-subiteration thinning algorithm for extracting medial lines
of Kalman Palagyi and Attila Kuba implementation
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

import numpy
# ==============================================================================


def _build_mask():
    M1 = numpy.array([[['x', 'x', '0'],
                       ['x', 'x', '0'],
                       ['x', 'x', '0']],

                      [['x', 'x', '0'],
                       ['1', '1', '0'],
                       ['x', 'x', '0']],

                      [['x', 'x', '0'],
                       ['x', 'x', '0'],
                       ['x', 'x', '0']]])

    M2 = numpy.array([[['.', '.', '0'],
                       ['.', '.', '0'],
                       ['.', '.', '0']],

                      [['.', '.', '0'],
                       ['1', '1', '0'],
                       ['.', '.', '0']],

                      [['.', '.', '.'],
                       ['.', '1', '.'],
                       ['.', '.', '.']]])

    M3 = numpy.array([[['.', '.', '0'],
                       ['.', '.', '0'],
                       ['.', '.', '.']],

                      [['.', '.', '0'],
                       ['1', '1', '0'],
                       ['.', '1', '.']],

                      [['.', '.', '.'],
                       ['.', '1', '.'],
                       ['.', '.', '.']]])

    M4 = numpy.array([[['.', '.', '0'],
                       ['.', '.', '0'],
                       ['.', '.', '0']],

                      [['.', '.', '0'],
                       ['1', '1', '0'],
                       ['.', '.', '0']],

                      [['.', '.', '0'],
                       ['.', '.', '0'],
                       ['.', '1', '1']]])

    M5 = numpy.array([[['0', '0', '0'],
                       ['0', '0', '0'],
                       ['0', '0', '0']],

                      [['x', 'x', '0'],
                       ['0', '1', '0'],
                       ['x', 'x', '0']],

                      [['x', 'x', '0'],
                       ['1', 'x', '0'],
                       ['x', 'x', '0']]])

    M6 = numpy.array([[['0', '0', '0'],
                       ['0', '0', '0'],
                       ['.', '.', '0']],

                      [['0', '0', '0'],
                       ['0', '1', '0'],
                       ['1', '.', '0']],

                      [['.', '.', '0'],
                       ['1', '.', '0'],
                       ['.', '.', '0']]])

    U = [M1, M2, M3, M4, M5, M6]

    D = list()
    for M in U:
        D.append(M[:, :, ::-1])

    W = list()
    N = list()
    E = list()
    S = list()

    for M in U:
        tmp = numpy.zeros_like(M)
        tmp[0, :, :] = numpy.rot90(M[0, :, :], 1)
        tmp[1, :, :] = numpy.rot90(M[1, :, :], 1)
        tmp[2, :, :] = numpy.rot90(M[2, :, :], 1)

        W.append(tmp)
        N.append(numpy.rot90(tmp))
        E.append(numpy.rot90(tmp, 2))
        S.append(numpy.rot90(tmp, 3))

    return U, D, N, S, E, W


def _check_mask(T, M):
    x_present = False
    x_ok = False
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if M[i, j, k] == '.':
                    continue
                if M[i, j, k] == '0' and T[i, j, k] != 0:
                    return False
                if M[i, j, k] == '1' and T[i, j, k] != 1:
                    return False
                if M[i, j, k] == 'x':
                    x_present = True
                    if T[i, j, k] == 1:
                        x_ok = True

    if x_present:
        if x_ok:
            return True
        else:
            return False
    else:
        return True


def _applied_masks(mat, masks):
    tmp = numpy.zeros_like(mat)
    xx, yy, zz = numpy.where(mat == 1)
    for i in range(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]
        block = mat[x - 1:x + 2, y - 1:y + 2, z - 1:z + 2]

        for mask in masks:
            if _check_mask(block, mask):
                tmp[x, y, z] = 1

    return mat - tmp


def skeletonize_thinning(img):
    """ A 3D 6-subiteration thinning algorithm for extracting medial lines
    of Kalman Palagyi and Attila Kuba implementation

    Parameters
    ----------
    img : ndarray, 3D

    Returns
    -------
    skeleton : ndarray
        The thinned image.
    """


    mat_len_x, mat_len_y, mat_len_z = img.shape
    mat_tmp = numpy.zeros((mat_len_x + 2, mat_len_y + 2, mat_len_z + 2),
                          dtype=int)
    mat_tmp[1:-1, 1:-1, 1:-1] = img.astype(int)

    U, D, N, S, E, W = _build_mask()

    # ==========================================================================

    j = 0
    while True:

        j += 1
        nb1 = numpy.count_nonzero(mat_tmp)
        mat_tmp = _applied_masks(mat_tmp, U)
        mat_tmp = _applied_masks(mat_tmp, D)
        mat_tmp = _applied_masks(mat_tmp, N)
        mat_tmp = _applied_masks(mat_tmp, S)
        mat_tmp = _applied_masks(mat_tmp, E)
        mat_tmp = _applied_masks(mat_tmp, W)

        nb2 = numpy.count_nonzero(mat_tmp)
        if nb1 == nb2:
            break

    # ==========================================================================

    return mat_tmp[1:-1, 1:-1, 1:-1]
