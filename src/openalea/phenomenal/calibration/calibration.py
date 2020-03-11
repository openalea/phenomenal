# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
""" This module contains a calibration model for phenoarch experiment
where a target is rotating instead of a plant in the image acquisition system.
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

import json
import math
import numpy
import scipy.optimize
from itertools import islice

from .frame import (Frame, x_axis, y_axis, z_axis)
from .transformations import (concatenate_matrices, rotation_matrix)

# ==============================================================================

__all__ = ["origin_axis",
           "CalibrationCamera",
           "CalibrationTarget",
           "CalibrationGuess",
           "CalibrationCameraTop",
           "Calibration",
           "CalibrationCameraSideWith2TargetYXZ"]


# ==============================================================================


def origin_axis(axes):
    """ Defines cam_origin_axis transformation matrix given a
    positioning of camera axes in the world frame

    :Parameters:
     - `axes` ([array,array,array]) - orientation of camera axes given as
                   the coordinates of the local axis in the global frame"""
    f = Frame(axes)
    rot = numpy.identity(4)
    rot[:3, :3] = f.rotation_to_global()
    return rot


def normalise_angle(angle):
    """normalise an angle to the [-pi, pi] range"""
    angle = numpy.array(angle)
    modulo = 2 * numpy.pi
    angle %= modulo
    # force to [0, modulo] range
    angle = (angle + modulo) % modulo
    return angle - numpy.where(angle > modulo / 2., modulo, 0)


class CalibrationCamera(object):
    """A class for calibration of Camera

    The camera is a a perfect pinhole camera associated to a 3d camera frame allowing its positioning in space.

     Camera and image frames are as depicted in
            https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html

    That is camera origin is image center, z-axis points toward the scene (camera optical axis), x+ is left-> right
    along image width, y+ is up->down along image height.
    Image frame origin is top-left, u is left->right along image width, v is up->down along image height
    """
    def __init__(self):
        # Camera Parameters
        self._cam_width_image = None
        self._cam_height_image = None
        self._cam_focal_length_x = None
        self._cam_focal_length_y = None
        self._cam_pos_x = None
        self._cam_pos_y = None
        self._cam_pos_z = None
        #  rotations from base_frame to local camera frame
        self._cam_rot_x = None
        self._cam_rot_y = None
        self._cam_rot_z = None

    def __str__(self):
        out = ''
        out += 'Camera Parameters : \n'
        out += '\tFocal length X : ' + str(self._cam_focal_length_x) + '\n'
        out += '\tFocal length Y : ' + str(self._cam_focal_length_y) + '\n'
        if self._cam_width_image is not None:
            out += '\tOptical Center X : ' + str(self._cam_width_image / 2.0) + '\n'
            out += '\tOptical Center Y : ' + str(self._cam_height_image / 2.0)
        else:
            out += '\tOptical Center X : ' + str(self._cam_width_image) + '\n'
            out += '\tOptical Center Y : ' + str(self._cam_height_image)
        out += '\n\n'

        out += '\tPosition X : ' + str(self._cam_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._cam_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._cam_pos_z) + '\n\n'

        out += '\tRotation X : ' + str(self._cam_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._cam_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._cam_rot_z) + '\n'

        return out

    @staticmethod
    def pixel_coordinates(point_3d,
                          width_image, height_image,
                          focal_length_x, focal_length_y):
        """ Compute image coordinates of a 3d point positioned in camera frame

        Args:
         - point (float, float, float): a point/array of points in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        pt = numpy.array(point_3d)
        x, y, z = pt.T

        u = x / z * focal_length_x + width_image / 2.0
        v = y / z * focal_length_y + height_image / 2.0

        if len(pt.shape) > 1:
            return numpy.column_stack((u, v))
        else:
            return u, v

    def get_pixel_coordinates(self):
        def pixel_coords(pts):
            return self.pixel_coordinates(pts, self._cam_width_image, self._cam_height_image,
                                          self._cam_focal_length_x, self._cam_focal_length_y)
        return pixel_coords

    @staticmethod
    def pixel_coordinates_2(point_3d, cx, cy, fx, fy):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        pt = numpy.array(point_3d)
        x, y, z = pt.T

        u = x / z * fx + cx
        v = y / z * fy + cy

        if len(pt.shape) > 1:
            return numpy.column_stack((u, v))
        else:
            return u, v

    @staticmethod
    def camera_frame(pos_x, pos_y, pos_z, rot_x, rot_y, rot_z):

        origin = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        rot = concatenate_matrices(mat_rot_x, mat_rot_y, mat_rot_z)

        return Frame(rot[:3, :3].T, origin)

    def get_camera_frame(self):
        return self.camera_frame(self._cam_pos_x, self._cam_pos_y, self._cam_pos_z, self._cam_rot_x, self._cam_rot_y,
                                 self._cam_rot_z)

    def set_vars(self, vars):
        for key, value in vars.items():
            setattr(self, key, value)

    def to_json(self):
        # d = vars(self)
        # d['_origin_axis'] = self._origin_axis.reshape(
        #     (16,)).tolist()
        save_class = {}
        save_class['cam_width_image'] = self._cam_width_image
        save_class['cam_height_image'] = self._cam_height_image
        save_class['cam_focal_length_x'] = self._cam_focal_length_x
        save_class['cam_focal_length_y'] = self._cam_focal_length_y
        save_class['cam_pos_x'] = self._cam_pos_x
        save_class['cam_pos_y'] = self._cam_pos_y
        save_class['cam_pos_z'] = self._cam_pos_z
        save_class['cam_rot_x'] = self._cam_rot_x
        save_class['cam_rot_y'] = self._cam_rot_y
        save_class['cam_rot_z'] = self._cam_rot_z

        return save_class

    @staticmethod
    def from_json(save_class):
        c = CalibrationCamera()
        # d['_origin_axis'] = numpy.array(
        #         d['_origin_axis']).reshape((4, 4)).astype(
        #         numpy.float32)
        # c.set_vars(d)
        c._cam_width_image = save_class['cam_width_image']
        c._cam_height_image = save_class['cam_height_image']
        c._cam_focal_length_x = save_class['cam_focal_length_x']
        c._cam_focal_length_y = save_class['cam_focal_length_y']
        c._cam_pos_x = save_class['cam_pos_x']
        c._cam_pos_y = save_class['cam_pos_y']
        c._cam_pos_z = save_class['cam_pos_z']
        c._cam_rot_x = save_class['cam_rot_x']
        c._cam_rot_y = save_class['cam_rot_y']
        c._cam_rot_z = save_class['cam_rot_z']

        return c

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

        c = CalibrationCamera.from_json(save_class)
        return c

    def dump(self, filename):
        save_class = self.to_json()
        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))


class CalibrationCameraTop(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False

        self._ref_target_points_local_3d = None
        self._ref_target_points_2d = None
        self._ref_target_points_3d = None

        self._ref_number = None

        # camera frame axis coordinates expressed in world coordinates
        axes = numpy.array([[1., 0., 0.],
                            [0., -1., 0.],
                            [0., 0., -1.]])

        self._cam_origin_axis = origin_axis(axes)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraTop()

            c._cam_width_image = save_class['cam_width_image']
            c._cam_height_image = save_class['cam_height_image']
            c._cam_focal_length_x = save_class['cam_focal_length_x']
            c._cam_focal_length_y = save_class['cam_focal_length_y']
            c._cam_pos_x = save_class['cam_pos_x']
            c._cam_pos_y = save_class['cam_pos_y']
            c._cam_pos_z = save_class['cam_pos_z']
            c._cam_rot_x = save_class['cam_rot_x']
            c._cam_rot_y = save_class['cam_rot_y']
            c._cam_rot_z = save_class['cam_rot_z']
            c._angle_factor = save_class['angle_factor']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

        return c

class CalibrationCameraSideWith2TargetYXZ(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None
        self._ref_number = None
        self._ref_target_1_points_2d = None
        self._ref_target_2_points_2d = None

        self._cam_pos_z = 0.0

        self._cam_rot_y = 0.0
        # camera frame axis coordinates expressed in world coordinates
        axes = numpy.array([[1., 0., 0.],
                            [0., 0., -1.],
                            [0., 1., 0.]])

        self._cam_origin_axis = origin_axis(axes)

        self._target_1_pos_x = None
        self._target_1_pos_y = None
        self._target_1_pos_z = None
        self._target_1_rot_x = None
        self._target_1_rot_y = None
        self._target_1_rot_z = None

        self._target_2_pos_x = None
        self._target_2_pos_y = None
        self._target_2_pos_z = None
        self._target_2_rot_x = None
        self._target_2_rot_y = None
        self._target_2_rot_z = None

    def __str__(self):
        out = ''
        out += CalibrationCamera.__str__(self)

        out += 'Target 1: \n'
        out += '\tPosition X : ' + str(self._target_1_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_1_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_1_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_1_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_1_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_1_rot_z) + '\n\n'

        out += 'Target 2: \n'
        out += '\tPosition X : ' + str(self._target_2_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_2_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_2_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_2_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_2_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_2_rot_z) + '\n\n'

        return out

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraSideWith2TargetYXZ()

            c._cam_width_image = save_class['cam_width_image']
            c._cam_height_image = save_class['cam_height_image']
            c._cam_focal_length_x = save_class['cam_focal_length_x']
            c._cam_focal_length_y = save_class['cam_focal_length_y']
            c._cam_pos_x = save_class['cam_pos_x']
            c._cam_pos_y = save_class['cam_pos_y']
            c._cam_pos_z = save_class['cam_pos_z']
            c._cam_rot_x = save_class['cam_rot_x']
            c._cam_rot_y = save_class['cam_rot_y']
            c._cam_rot_z = save_class['cam_rot_z']
            c._angle_factor = save_class['angle_factor']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

            if 'targets_parameters' not in save_class:
                c._target_1_pos_x = save_class['target_1_pos_x']
                c._target_1_pos_y = save_class['target_1_pos_y']
                c._target_1_pos_z = save_class['target_1_pos_z']
                c._target_1_rot_x = save_class['target_1_rot_x']
                c._target_1_rot_y = save_class['target_1_rot_y']
                c._target_1_rot_z = save_class['target_1_rot_z']

                c._target_2_pos_x = save_class['target_2_pos_x']
                c._target_2_pos_y = save_class['target_2_pos_y']
                c._target_2_pos_z = save_class['target_2_pos_z']
                c._target_2_rot_x = save_class['target_2_rot_x']
                c._target_2_rot_y = save_class['target_2_rot_y']
                c._target_2_rot_z = save_class['target_2_rot_z']
            else:
                t1, t2 = save_class['targets_parameters']
                c._target_1_pos_x = t1['_pos_x']
                c._target_1_pos_y = t1['_pos_y']
                c._target_1_pos_z = t1['_pos_z']
                c._target_1_rot_x = t1['_rot_x']
                c._target_1_rot_y = t1['_rot_y']
                c._target_1_rot_z = t1['_rot_z']

                c._target_2_pos_x = t2['_pos_x']
                c._target_2_pos_y = t2['_pos_y']
                c._target_2_pos_z = t2['_pos_z']
                c._target_2_rot_x = t2['_rot_x']
                c._target_2_rot_y = t2['_rot_y']
                c._target_2_rot_z = t2['_rot_z']

        return c


class CalibrationTarget(object):
    """A class for target objects used for calibration

    The local target frame origin is target center,right being left-> right along target width and y+ bottom->up
            along target height
    """
    def __init__(self, label='target'):
        self._label = label
        self._pos_x = None
        self._pos_y = None
        self._pos_z = None
        self._rot_x = None
        self._rot_y = None
        self._rot_z = None

    def set_vars(self, vars):
        for key, value in vars.items():
            setattr(self, key, value)

    def to_json(self):
        d = vars(self)
        return d

    @staticmethod
    def from_json(d):
        ct = CalibrationTarget()
        ct.set_vars(d)
        return ct

    @staticmethod
    def target_frame(pos_x, pos_y, pos_z, rot_x, rot_y, rot_z):

        origin  = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        rot = concatenate_matrices(mat_rot_z, mat_rot_x, mat_rot_y)

        return Frame(rot[:3, :3].T, origin)

    def get_target_frame(self):
        return self.target_frame(self._pos_x, self._pos_y, self._pos_z, self._rot_x, self._rot_y, self._rot_z)

    def __str__(self):
        out = ''
        out += self._label + ': \n'
        out += '\tPosition X : ' + str(self._pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._rot_z) + '\n\n'
        return out


class CalibrationGuess(object):
    """Methods for guessing/setting configuration of a multiview system"""
    def __init__(self, cameras, targets):
        """

        Args:
            cameras:[(type, distance, image_size, resolution), ...] : a list of guessed parameters for cameras.
            type controls rought camera orientation and position ('side' or 'top'), distance is the distance to the
            axis of rotation (world unit), image size is a (width, heigth) tuple and resolution an estimate of the
            camera resolution (pixel per world unit) near the axis of rotation
            targets: [(type, distance, azimuth, inclination), ...]: a list of guessed parameters for targets.
            type controls rought target orientation and position ('side' or 'top'), distance is the distance to the
            axis of rotation (world unit), azimuth and inclination the rotation angle (deg)
        """

        self.cameras = []
        self.targets = []

        for ctype, distance, im_size, resolution in cameras:
            c = CalibrationCamera()
            w, h = im_size
            f = resolution * distance
            px, py, pz = 0, 0, 0
            rx, ry, rz = 0, 0, 0
            if ctype == 'side':
                py -= distance
                rx -= numpy.pi /2.
            elif ctype == 'top':
                pz += distance
                rx += numpy.pi
            c._cam_width_image = w
            c._cam_height_image = h
            c._cam_focal_length_x = f
            c._cam_focal_length_y = f
            c._cam_pos_x = px
            c._cam_pos_y = py
            c._cam_pos_z = pz
            c._cam_rot_x = rx
            c._cam_rot_y = ry
            c._cam_rot_z = rz
            c._angle_factor = 1
            c._cam_origin_axis = numpy.identity(4)
            self.cameras.append(c)

        for ttype, distance, azimuth, inclination in targets:
            t = CalibrationTarget()
            px, py, pz = 0, 0, 0
            rx, ry, rz = numpy.radians(- inclination), 0, 0
            if ttype == 'side':
                py -= distance
                rx += numpy.pi / 2.
            elif ttype == 'top':
                pz += distance
            azimuth = numpy.radians(azimuth)
            px, py, pz = [
                px * math.cos(azimuth) - py * math.sin(azimuth),
                px * math.sin(azimuth) + py * math.cos(azimuth),
                pz]
            rz += azimuth

            t._pos_x = px
            t._pos_y = py
            t._pos_z = pz
            t._rot_x = rx
            t._rot_y = ry
            t._rot_z = rz
            self.targets.append(t)

def guess_from_chess(chess):
    """
    for facing angle : max(area) + max yc (normalisee
    target azimuth = facing angle + facing angle reference camera
    caera azimuth : target azimuth + facing angle
    for resolution : area of facing
    for camera elevation : excentricity
    for target inclination : area of two constrasting camera position

    => guess from chessboard + camera distance to center of targets only
    Args:
        chess:

    Returns:

    """
    pts = chess.get_corners_2d('side')
    yc = {ang: (a[0, 1] + a[-1, 1]) / 2. for ang, a in pts.items()}
   # alpha = yc.keys()[numpy.argmax(yc.values())]


class Calibration(object):
    """A class for calibration of multiview imaging systems (fixed cameras, rotating target)"""

    def __init__(self, reference_camera='side', angle_factor=1, clockwise_rotation=True,
                 fit_angle_factor = True, fit_reference_camera = True, fit_targets = True, fit_cameras = True,
                 verbose=False):
        """
       Instantiate a Calibration object

        Args:
            nb_targets: (int) number of targets
            nb_cameras: (int) number of cameras
            reference_camera: ('camera' or 'target') reference used to define world y-axis together with base frames for
             expressing the rotations of camera and targets(see details)
            clockwise_rotation: (bool) : are targets rotating clockwise ? (default True)
            : Absolute value of the angle of rotation of the turntable at the time of
             image acquisition
        Details:
            Calibration allows the projection of world 3D points on 2D images, using calibration targets. Points of
            the world are given in a world global frame, defined by the axis of rotation and a reference object (the
            first camera or the first target).
            The axis of rotation of the rotating system, oriented toward the sky, defines the world z-axis.
            The altitude of the first camera defines the position of the world origin on z-axis.
            If reference_object='camera' (default), the y-axis is given by camera position and world origin and y+
              is directed is from camera toward z-axis
            If reference_object='target' (useful alternative if the reference camera lies on the axis of rotation),
              the y+ axis is given by the projection on a plane, perpendicular to the axis of rotation, of the y+ axis
              of the local frame associated to the first target.

            Base frames offers convenient ways for expressing/checking the orientation angles of cameras and targets.
            If reference_object='camera' (default), the base frame (rot_x = rot_y = rot_z = 0) for cameras correspond
              to a 'vertical' camera (image plane parallel to xz plane) pointing at the axis of rotation (camera optical
              axis aligned with y+), and the base frame for targets to a 'vertical' target facing the camera base frame
              (x+_target = x+_world, y+_target = z+_world)
            If reference_object='target', the base frame (rot_x = rot_y = rot_z = 0) for cameras correspond to a
             'horizontal' camera (image plane parallel to world xy plane) pointing downward (camera optical axis
              aligned with z-), and the base frame for targets to an 'horizontal' target  facing the camera base frame
              (x+_target = x+_world, y+_target = y+_world)
        """

        self._verbose = verbose
        self.clockwise = clockwise_rotation
        self.angle_factor = angle_factor
        self.fit_angle_factor = fit_angle_factor
        self.fit_reference_camera = fit_reference_camera
        self.fit_targets = fit_targets
        self.fit_cameras = fit_cameras
        self.reference_camera = reference_camera
        # targets corner points coordinates expressed in targets local frame
        self._targets_points = []

        self._nb_targets = 0
        # label = 'target_'
        self._targets = []
        # self._ref_cam = CalibrationCamera()

        # cameras
        self._nb_cameras = 0
        self._cameras = {}
        # total number of target corners points
        self._nb_image_points = 0
        self._image_points = {}

    def __str__(self):
        out = 'Calibration:\n'

        for id_camera, camera in self._cameras.items():
            out += 'Camera {}'.format(id_camera)
            if id_camera == self.reference_camera:
                out += ' (reference)'
            out += ': \n'
            out += str(camera)

        for i, target in enumerate(self._targets):
            out += 'Target {}: \n'.format(i)
            out += str(target)

        return out

    @staticmethod
    def turntable_frame(rotation, angle_factor=1, clockwise=True):
        """ Frame attached to turntable. This correspond to world frame rotated.

        Args:
            rotation: the rotation consign of the turning table
            angle_factor: a float multiplier of rotation consign to obtain actual rotation angle
            clockwise: is turntable rotating clockwise ?

        Returns:
            a frame object
        """

        alpha = numpy.radians(rotation * angle_factor)
        if clockwise:
            alpha *= -1

        return Frame([(numpy.cos(alpha), numpy.sin(alpha), 0),
                      (-numpy.sin(alpha), numpy.cos(alpha), 0),
                      (0, 0, 1)])

    def get_turntable_frame(self, rotation):
        return self.turntable_frame(rotation, self.angle_factor, self.clockwise)

    def get_projection(self, id_camera, rotation):

        camera = self._cameras[id_camera]
        fr_cam = camera.get_camera_frame()
        fr_table = self.get_turntable_frame(rotation)
        pixel_coords = camera.get_pixel_coordinates()

        def projection(pts):
            # rotated pts
            rotated = fr_table.global_point(pts)
            return pixel_coords(fr_cam.local_point(rotated))

        return projection

    def split_parameters(self, x0):
        # decompose x0 into angle_factor, reference camera, targets and cameras list of parameters
        # number of parameters per above mentioned items
        nbp_target = 6
        nbp_camera = 8
        nb_pars = [0, 0, 0, 0]
        if self.fit_angle_factor:
            nb_pars[0] = 1
        if self.fit_reference_camera:
            nb_pars[1] = 6
        if self.fit_targets:
            nb_pars[2] = nbp_target * self._nb_targets
        if self.fit_cameras:
            nb_pars[3] = nbp_camera * (self._nb_cameras - 1) # minus reference camera
        xx0 = iter(x0)
        turntable, ref_cam, targets, cameras = [list(islice(xx0, n)) for n in nb_pars]
        # further group per target and per camera
        targetss = []
        for i in range(0, len(targets), nbp_target):
            targetss.append(targets[i: i + nbp_target])
        camerass = []
        for i in range(0, len(cameras), nbp_camera):
            camerass.append(cameras[i: i + nbp_camera])

        return turntable, ref_cam, targetss, camerass

    def fit_function(self, x0):

        turntable, ref_cam, targets, cameras = self.split_parameters(x0)

        # merge ref_cam to cameras
        if len(ref_cam) > 0:
            cam_pos_x = 0
            cam_pos_z = 0
            cam_focal_length_x, cam_focal_length_y, \
            cam_pos_y, \
            cam_rot_x, cam_rot_y, cam_rot_z = ref_cam
            ref_cam = [cam_focal_length_x, cam_focal_length_y,
                       cam_pos_x, cam_pos_y, cam_pos_z,
                       cam_rot_x, cam_rot_y, cam_rot_z]
            cameras.insert(0, ref_cam)

        # build frames
        angle_factor = self.angle_factor
        if len(turntable) > 0:
            angle_factor = turntable[0]

        target_frames = []
        if len(targets) > 0:
            for target in targets:
                pos_x, pos_y, pos_z, rot_x, rot_y, rot_z = target
                target_frames.append(CalibrationTarget.target_frame(pos_x, pos_y, pos_z, rot_x, rot_y, rot_z))
        else:
            for target in self._targets:
                target_frames.append(target.get_target_frame())

        camera_frames = []
        camera_focals = []
        for camera in cameras:
            cam_focal_length_x, cam_focal_length_y, \
            cam_pos_x, cam_pos_y, cam_pos_z, \
            cam_rot_x, cam_rot_y, cam_rot_z = camera
            camera_frames.append(CalibrationCamera.camera_frame(cam_pos_x, cam_pos_y, cam_pos_z,
                                                            cam_rot_x, cam_rot_y, cam_rot_z))
            camera_focals.append([cam_focal_length_x, cam_focal_length_y])

        err = 0
        # cameras and image_points in the right order
        cams = []
        im_pts_cam = []
        if len(ref_cam) > 0:
            cams += [self._cameras[self.reference_camera]]
            im_pts_cam += [self._image_points[self.reference_camera]]
        cams += [self._cameras[k] for k in self._cameras if k is not self.reference_camera]
        im_pts_cam += [self._image_points[k] for k in self._cameras if k is not self.reference_camera]

        for fr_cam, focals, camera, im_pts_c in zip(camera_frames, camera_focals, cams, im_pts_cam):
            for fr_target, t_pts, im_pts in zip(target_frames, self._targets_points, im_pts_c):
                for rotation, ref_pts in im_pts.items():
                    fr_table = Calibration.turntable_frame(rotation, angle_factor, self.clockwise)
                    target_pts = fr_table.global_point(fr_target.global_point(t_pts))
                    cam_focal_length_x, cam_focal_length_y = focals
                    pts = CalibrationCamera.pixel_coordinates(fr_cam.local_point(target_pts),
                                                              camera._cam_width_image,
                                                              camera._cam_height_image,
                                                              cam_focal_length_x,
                                                              cam_focal_length_y)
                    err += numpy.linalg.norm(
                        numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print(err)

        return err

    def get_parameters(self):
        parameters = []
        if self.fit_angle_factor:
            parameters.append(self.angle_factor)
        if self.fit_reference_camera:
            c = self._cameras[self.reference_camera]
            parameters += [c._cam_focal_length_x, c._cam_focal_length_y,
                           c._cam_pos_y,
                           c._cam_rot_x, c._cam_rot_y, c._cam_rot_z]
        if self.fit_targets:
            for t in self._targets:
                parameters += [t._pos_x,
                               t._pos_y,
                               t._pos_z,
                               t._rot_x,
                               t._rot_y,
                               t._rot_z]
        if self.fit_cameras:
            for id_camera, c in self._cameras.items():
                if id_camera is not self.reference_camera:
                    parameters += [c._cam_focal_length_x,
                                   c._cam_focal_length_y,
                                   c._cam_pos_x,
                                   c._cam_pos_y,
                                   c._cam_pos_z,
                                   c._cam_rot_x,
                                   c._cam_rot_y,
                                   c._cam_rot_z]
        return parameters


    def find_parameters(self):

        start = self.get_parameters()
        parameters = scipy.optimize.minimize(
            self.fit_function,
            start,
            method='BFGS').x

        err = self.fit_function(parameters)

        if self._verbose:
            print('Result : ', parameters)
            print('Err : ', err / self._nb_image_points)

        return parameters

    def calibration_error(self):
        p = self.get_parameters()
        return self.fit_function(p) / self._nb_image_points

    def get_target_projected(self, i_camera, i_target, rotation):

        proj = self.get_projection(i_camera, rotation)
        target_pts = self.get_target_points(i_target)

        return proj(target_pts)

    def get_target_points(self, i_target):
        fr_target = self._targets[i_target].get_target_frame()
        return fr_target.global_point(self._targets_points[i_target])

    def setup_calibrate(self,
                        targets=None,
                        target_points=None,
                        cameras=None,
                        image_points=None):
        if targets is not None:
            self._targets = targets
        if target_points is not None:
            self._targets_points = target_points
        if cameras is not None:
            self._cameras = cameras
        if image_points is not None:
            self._image_points = image_points

        self._nb_cameras = len(self._cameras)
        self._nb_targets = len(self._targets)
        self._nb_image_points = 0
        for cam_pts in self._image_points.values():
            for im_pts_t in cam_pts:
                for im_pts in im_pts_t.values():
                    self._nb_image_points += len(im_pts)

    def calibrate(self,
                  targets=None,
                  target_points=None,
                  cameras=None,
                  image_points=None):
        """ Optimise the cameras and targets parameters to minimise the distance between
       observed image points and projections on images of target points

        Args:
            targets: A list of CalibrationTarget objects to be used as start guess for targets
            target_points: A list of coordinates of target corner points, expressed in local
             target frame
            cameras: A list of CalibrationCamera objects, to be used as start guess for cameras
            image_points: {id_camera #ICI#)

        Returns:

        """
        self.setup_calibrate(targets, target_points, cameras, image_points)
        parameters = self.find_parameters()
        turntable, ref_cam, target_pars, camera_pars = self.split_parameters(parameters)

        if len(turntable) >0:
            self.angle_factor = turntable[0]

        if len(ref_cam) > 0:
            camera = self._cameras[self.reference_camera]
            labels = ['_cam_focal_length_x', '_cam_focal_length_y',
                      '_cam_pos_y',
                      '_cam_rot_x', '_cam_rot_y', '_cam_rot_z']
            d = dict(zip(labels, ref_cam))
            for k in d:
                if k.startswith('_cam_rot'):
                    d[k] = normalise_angle(d[k])
            camera.set_vars(d)

        if len(target_pars) > 0:
            labels = ['_pos_x', '_pos_y', '_pos_z',
                      '_rot_x', '_rot_y', '_rot_z']
            for target, target_param in zip(self._targets, target_pars):
                d = dict(zip(labels, target_param))
                for k in d:
                    if k.startswith('_rot'):
                        d[k] = normalise_angle(d[k])
                target.set_vars(d)

        if len(camera_pars) > 0:
            cams = [self._cameras[k] for k in self._cameras if k is not self.reference_camera]
            for camera, camera_param in zip(cams, camera_pars):
                labels = ['_cam_focal_length_x', '_cam_focal_length_y',
                          '_cam_pos_x', '_cam_pos_y', '_cam_pos_z',
                          '_cam_rot_x', '_cam_rot_y', '_cam_rot_z']
                d = dict(zip(labels, camera_param))
                for k in d:
                    if k.startswith('_cam_rot'):
                        d[k] = normalise_angle(d[k])
                camera.set_vars(d)

        err = self.fit_function(parameters)

        return err / self._nb_image_points

    def dump(self, filename):
        save_class = dict()
        save_class['angle_factor'] = self.angle_factor
        save_class['clockwise'] = self.clockwise
        save_class['reference_camera'] = self.reference_camera
        save_class['cameras_parameters'] = {id_camera: camera.to_json() for id_camera,camera in self._cameras.items()}
        save_class['targets_parameters'] = [t.to_json() for t in self._targets]

        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

        c = Calibration()
        c._cameras = {id_camera: CalibrationCamera.from_json(pars) for id_camera, pars in save_class['cameras_parameters'].items()}
        c._targets = [CalibrationTarget.from_json(pars) for pars in save_class['targets_parameters']]
        c._nb_cameras = len(c._cameras)
        c._nb_targets = len(c._targets)
        c.angle_factor = save_class['angle_factor']
        c.clockwise = save_class['clockwise']
        c.reference_camera = save_class['reference_camera']
        return c


def find_position_3d_points(pt2d, calibrations):
    def fit_function(x0):

        sum_err = 0
        vec_err = list()
        for id_camera in pt2d:
            for angle in pt2d[id_camera]:
                if id_camera in calibrations:
                    calib = calibrations[id_camera]
                    fr_cam = calib.camera_frame(calib._cam_pos_x, calib._cam_pos_y, calib._cam_pos_z, calib._cam_rot_x,
                                                calib._cam_rot_y, calib._cam_rot_z)

                    pos_x, pos_y, pos_z = x0
                    alpha = math.radians(angle * calib._angle_factor)

                    origin = [pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
                              pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
                              pos_z]

                    pt = calibrations[id_camera].pixel_coordinates(
                        fr_cam.local_point(origin),
                        calib._cam_width_image,
                        calib._cam_height_image,
                        calib._cam_focal_length_x,
                        calib._cam_focal_length_y)

                    err = numpy.linalg.norm(
                        numpy.array(pt) - pt2d[id_camera][angle]).sum()

                    # vec_err.append(err)
                    sum_err += err

        # return vec_err
        return sum_err

    parameters = [0.0] * 3
    parameters = scipy.optimize.basinhopping(fit_function, parameters).x

    print("Err : ", fit_function(parameters))
    return parameters


def find_position_3d_points_soil(pts, calibrations, verbose=False):
    def soil_frame(pos_x, pos_y, pos_z,
                   rot_x, rot_y, rot_z):

        origin = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        rot = concatenate_matrices(mat_rot_x, mat_rot_y, mat_rot_z)

        return Frame(rot[:3, :3].T, origin)

    def err_projection(x0, verbose=False):
        err = 0

        sf = soil_frame(0, 0, x0[0],
                        x0[1], x0[2], x0[3])

        for i in range(len(pts)):
            pt2d = pts[i]
            for id_camera in pt2d:
                for angle in pt2d[id_camera]:
                    if id_camera in calibrations:
                        calib = calibrations[id_camera]
                        fr_cam = calib.camera_frame(calib._cam_pos_x, calib._cam_pos_y, calib._cam_pos_z,
                                                    calib._cam_rot_x, calib._cam_rot_y, calib._cam_rot_z)

                        pos_x, pos_y, pos_z = sf.global_point(
                            (x0[4 + i * 2], x0[5 + i * 2], 0))
                        alpha = math.radians(angle * calib._angle_factor)

                        origin = [pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
                                  pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
                                  pos_z]

                        pt = calib.pixel_coordinates(
                            fr_cam.local_point(origin),
                            calib._cam_width_image,
                            calib._cam_height_image,
                            calib._cam_focal_length_x,
                            calib._cam_focal_length_y)

                        err += numpy.linalg.norm(
                            numpy.array(pt) - pt2d[id_camera][angle]).sum()

                        if verbose:
                            print("ID CAMERA & ANGLE", id_camera, angle)
                            print('PT 3D : ', pos_x, pos_y, pos_z)
                            print("Projection image 2D", pt)
                            print("Ref image 2D", pt2d[id_camera][angle])
                            print("Distance :", numpy.linalg.norm(
                                numpy.array(pt - pt2d[id_camera][angle]).sum()))
                            print("\n\n")

        print(err)
        return err

    def fit_function(x0):
        return err_projection(x0)

    parameters = [0, 0, 0, 0]
    parameters += [0] * 2 * len(pts)

    parameters = scipy.optimize.basinhopping(
        fit_function, parameters, niter=10).x

    for i in [1, 2, 3]:
        parameters[i] %= math.pi * 2.0

    if verbose:
        print("Err : ", err_projection(parameters, verbose=True))

    sf = soil_frame(0, 0, parameters[0],
                    parameters[1], parameters[2], parameters[3])

    return parameters, sf
