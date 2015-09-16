""" This module contains a calibration model
for phenoarch experiment where a chessboard is rotating
instead of a plant in a picture cabin.
"""
from math import atan2, cos, pi, sin, radians, degrees
from numpy import array, dot
from numpy.linalg import norm

from frame import Frame, x_axis, y_axis, z_axis
from transformations import (concatenate_matrices,
                             rotation_matrix,
                             translation_matrix)

def chess_corners(chessboard):
    square_size = chessboard.square_size
    width, height = chessboard.shape

    chessboard_pts = []
    for j in range(height):
        for i in range(width):
            v = array([i * square_size, j * square_size, 0.])
            chessboard_pts.append(v)

    return chessboard_pts


def chess_frame(x, y, z, elev, tilt):
    """ Compute local frame associated to chessboard

    Args:
     - x (float): x position of chess in world frame
     - y (float): y position of chess in world frame
     - z (float): z position of chess in world frame
     - elev (float): elevation angle around local x axis
     - tilt (float): rotation angle around local z axis
    """
    origin = [x , y, z]

    shift = rotation_matrix(-pi / 2., x_axis)

    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)
    rot = concatenate_matrices(shift, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)


def camera_frame(dist, offset, z, azim, elev, tilt, offset_angle, alpha):
    """ Compute local frame associated to the camera

    Args:
     - dist (float): distance of camera to rotation axis
     - offset (float): offset angle in radians for rotation
     - z (float): z position of cam in world frame when alpha=0
     - azim (float): azimuth angle of camera (around local y axis)
     - elev (float): elevation angle of camera (around local x axis)
     - tilt (float): tilt angle of camera (around local z axis)
     - offset_angle (float): rotation offset around z_axis in world frame
                              (i.e. rotation angle of camera when alpha=0)
     - alpha (float): rotation angle around z_axis in world frame
    """
    origin = (dist * cos(alpha + offset),
              dist * sin(alpha + offset),
              z)

    shift = rotation_matrix(-pi / 2., x_axis)
    rot_y = rotation_matrix(-alpha + offset_angle, y_axis)

    mat_azim = rotation_matrix(azim, y_axis)
    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)

    rot = concatenate_matrices(shift, rot_y, mat_azim, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)
