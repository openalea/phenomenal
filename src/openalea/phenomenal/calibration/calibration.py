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
from copy import deepcopy

from .frame import (Frame, x_axis, y_axis, z_axis)
from .transformations import (concatenate_matrices, rotation_matrix)

# ==============================================================================

__all__ = ["CalibrationCamera",
           "CalibrationFrame",
           "CalibrationSetup",
           "Calibration",
           "OldCalibrationCamera",
           "load_old_calibration"]


# ==============================================================================


def normalise_angle(angle):
    """normalise an angle to the [-pi, pi] range"""
    angle = numpy.array(float(angle))
    modulo = 2 * numpy.pi
    angle %= modulo
    # force to [0, modulo] range
    angle = (angle + modulo) % modulo
    return angle - numpy.where(angle > modulo / 2., modulo, 0)


class CalibrationFrame(object):
    """A class for objects with local frames used for calibration

    The object local frame is a translated / rotated transform of the world frame around (fixed) world axis.
    """
    def __init__(self):
        self._pos_x = None
        self._pos_y = None
        self._pos_z = None
        self._rot_x = None
        self._rot_y = None
        self._rot_z = None

    def set_vars(self, d):
        for key, value in d.items():
            setattr(self, key, value)

    def to_json(self):
        d = vars(self)
        return d

    @staticmethod
    def from_json(d):
        cf = CalibrationFrame()
        cf.set_vars(d)
        return cf

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

        c = CalibrationFrame.from_json(save_class)
        return c

    def dump(self, filename):
        save_class = self.to_json()
        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def frame(pos_x, pos_y, pos_z, rot_x, rot_y, rot_z):

        origin = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        fr_x = Frame(mat_rot_x[:3, :3].T)
        fr_y = Frame(mat_rot_y[:3, :3].T)
        fr_z = Frame(mat_rot_z[:3, :3].T)

        axes = fr_z.global_point(fr_y.global_point(fr_x.global_point((x_axis, y_axis, z_axis))))

        return Frame(axes, origin)

    def get_frame(self):
        return self.frame(self._pos_x, self._pos_y, self._pos_z, self._rot_x, self._rot_y, self._rot_z)

    def get_extrinsic(self):
        extrinsic = numpy.identity(4)
        fr = self.get_frame()
        extrinsic[:3, :3] = fr.rotation_to_local()
        extrinsic[:3, 3] = fr.local_point((0, 0, 0))
        return extrinsic[:3, ]

    def __str__(self):
        out = ''
        out += '\tPosition X : ' + str(self._pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._pos_z) + '\n\n'
        out += '\tRotation X : {} rad / {} deg\n'.format(self._rot_x, numpy.degrees(self._rot_x))
        out += '\tRotation Y : {} rad / {} deg\n'.format(self._rot_y, numpy.degrees(self._rot_y))
        out += '\tRotation Z : {} rad / {} deg\n\n'.format(self._rot_z, numpy.degrees(self._rot_z))

        return out


class CalibrationCamera(CalibrationFrame):
    """A class for calibration of Camera

    The camera is a a perfect pinhole camera associated to a calibrationframe allowing its positioning in space.

     Camera and image frames are as depicted in
            https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html

    That is camera frame origin is image center, z-axis points toward the scene (camera optical axis),
    x+ is left-> right along image width, y+ is up->down along image height.
    Image frame origin is top-left, u is left->right along image width, v is up->down along image height
    """
    def __init__(self):
        CalibrationFrame.__init__(self)
        # Camera Parameters
        self._width_image = None
        self._height_image = None
        self._focal_length_x = None
        self._focal_length_y = None

    def __str__(self):
        out = ''
        out += '\tFocal length X : ' + str(self._focal_length_x) + '\n'
        out += '\tFocal length Y : ' + str(self._focal_length_y) + '\n'
        if self._width_image is not None:
            out += '\tOptical Center X : ' + str(self._width_image / 2.0) + '\n'
            out += '\tOptical Center Y : ' + str(self._height_image / 2.0)
        else:
            out += '\tOptical Center X : ' + str(self._width_image) + '\n'
            out += '\tOptical Center Y : ' + str(self._height_image)
        out += '\n\n'
        out += CalibrationFrame.__str__(self)

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
            return self.pixel_coordinates(pts, self._width_image, self._height_image,
                                          self._focal_length_x, self._focal_length_y)
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

    def get_projection(self):
        fr_cam = self.get_frame()
        pixel_coords = self.get_pixel_coordinates()

        def projection(pts):
            return pixel_coords(fr_cam.local_point(pts))

        return projection

    def get_intrinsic(self):
        intrinsic = numpy.identity(3)
        fx = self._focal_length_x
        fy = self._focal_length_y
        cx = self._width_image / 2.
        cy = self._height_image / 2.
        di = numpy.diag_indices(2)
        intrinsic[:2, 2] = (cx, cy)
        intrinsic[di] = (fx, fy)
        return intrinsic

    @staticmethod
    def from_json(save_class):
        c = CalibrationCamera()
        c.set_vars(save_class)
        return c

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)
        if 'cam_pos_x' in save_class:
            raise ValueError('Old style calibration should now  be loaded with OldCalibrationCamera.load method')
        c = CalibrationCamera.from_json(save_class)
        return c


class CalibrationSetup(object):
    """A class for helping the setup of a multi-view imaging systems to be calibrated"""

    def __init__(self, cameras=None, targets=None, image_resolutions=None, image_sizes=None, facings=None,
                 clockwise_rotation=True):
        """ Intantiate a CalibrationSetup for positioning cameras and targets of a multiview acquisition system

        Args:
            cameras:{camera_id: (distance, inclination), ...}: a dict of parameters for positioning cameras in the
                system. distance is the distance to the axis of rotation (word units), along camera
                optical axis. inclination is the angle (degree, positive) between world z+ (axis of rotation) and
                camera z- (z-axis being optical axis).
            targets: {target_id: (distance, inclination), ...}: a dict of parameters for positioning targets.
                distance is the distance to the axis of rotation (word units), along target normal direction.
                inclination is the angle (degree, positive) between world z+ (axis of rotation) and target normal.
            image_resolutions: a {camera_id: resolution, ...} dict of image resolution (pixel per world unit) for an
                object located near the axis of rotation
            image_sizes is a {camera_id: (width, height), ...} dict giving image dimension in pixels
            facings : a {target_id: {camera_id: angle, ...}, ...} dict of dict giving the rotation consigns
                (degree, positive) for which a chessboard is facing a camera (ie with with topleft corner closest to
                 topleft side of the image).
            clockwise_rotation (bool): are targets rotating clockwise ? (default True)

        """

        self.cameras = cameras
        self.targets = targets
        self.image_resolutions = image_resolutions
        self.image_sizes = image_sizes
        self.facings = facings
        self.clockwise = clockwise_rotation
        self.world_origin = 0
        self.reference_target_facing = 0

    def setup_calibration(self, reference_camera, reference_target):
        """ Setup the cameras and targets

        Args:
            reference_camera (str): the camera_id of the camera to be used to define world frame (cf Calibration)
            reference_target (str): the target_id of the target to be used to position cameras

        Returns:
            targets and cameras

        """
        cams, targs = {}, {}

        self.reference_target_facing = self.facings[reference_target][reference_camera]
        # determine setup world origin
        distance, inclination = self.cameras[reference_camera]
        ref_cam = self.setup_camera(inclination=inclination, facing=self.reference_target_facing, distance=distance)
        self.world_origin = ref_cam._pos_z

        # build targets
        for id_target, target in self.targets.items():
            distance, inclination = target
            facing = self.facings[id_target][reference_camera]
            targs[id_target] = self.setup_target(inclination=inclination, facing=facing, distance=distance)

        # build cameras
        for id_camera, camera in self.cameras.items():
            distance, inclination = camera
            facing = self.facings[reference_target][id_camera]
            image_size = self.image_sizes[id_camera]
            resolution = self.image_resolutions[id_camera]
            cams[id_camera] = self.setup_camera(image_size=image_size, resolution=resolution,
                                                        inclination=inclination, facing=facing, distance=distance)

        return cams, targs, reference_camera, self.clockwise

    def alpha(self, rotation):
        angle = numpy.radians(rotation)
        if self.clockwise:
            angle *= -1
        return angle

    def setup_target(self, inclination=0, facing=0, distance=0):
        """ setup a target frame

        Args:
            inclination: the angle (degree, positive) between world z+ (axis of rotation) and target normal. By
                default, inclination = 0, that corresponds to a horizontal target
            facing: the rotation consign (degree, positive) for which the chessboard is facing the reference camera
                (ie with with topleft corner closest to topleft side of the image).
            distance: the distance to the axis of rotation (word units), along target normal direction.

        Returns:
            A CalibrationFrame positioned in world frame

        """

        # starting frame : frame axis = world axis, ie horizontal target facing reference camera when facing = 0
        px, py, pz = 0, 0, 0
        rx, ry, rz = 0, 0, 0
        rx += numpy.radians(inclination)
        rz -= self.alpha(facing)
        fr = CalibrationFrame.frame(px, py, pz, rx, ry, rz)
        px, py, pz = fr.global_point((0, 0, distance))
        #
        pz -= self.world_origin
        #
        c = CalibrationFrame()
        c._pos_x, c._pos_y, c._pos_z = px, py, pz
        c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx),  normalise_angle(ry), normalise_angle(rz)

        return c

    def setup_camera(self, image_size=None, resolution=None, inclination=0, facing=0, distance=0):
        """ setup a calibration camera from simple inputs

        Args:
            image_size:
            resolution: image resolution (pixel per world unit) for an object located near the axis of rotation
            inclination: the angle (degree, positive) between world z+ (axis of rotation) and camera z- (opposite
            optical axis) . By default, inclination = 0, that corresponds to a camera pointing downwards
            facing: the rotation consign (degree, positive) for which the reference target is facing the camera
                (ie with with top left corner closest to top left side of the image).
            distance: the distance to the axis of rotation (word units), along camera optical axis.

        Returns:
            A CalibrationCamera positioned in calibration world frame

        """

        w, h, f = None, None, None
        if image_size is not None and resolution is not None:
            w, h = image_size
            f = resolution * distance

        # starting frame: pi rotation around x of world frame, ie camera facing horizontal target aligned with world
        # axis
        px, py, pz = 0, 0, 0
        rx, ry, rz = numpy.pi, 0, 0
        rx += numpy.radians(inclination)
        rz += self.alpha(facing - self.reference_target_facing)
        fr = CalibrationFrame.frame(px, py, pz, rx, ry, rz)
        px, py, pz = fr.global_point((0, 0, -distance))
        #
        pz -= self.world_origin

        c = CalibrationCamera()
        c._width_image, c._height_image = w, h
        c._focal_length_x, c._focal_length_y = f, f
        c._pos_x, c._pos_y, c._pos_z = px, py, pz
        c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx),  normalise_angle(ry), normalise_angle(rz)

        return c


class Calibration(object):
    """A class for calibration of multi-views imaging systems (fixed cameras, rotating targets)"""

    def __init__(self, angle_factor=1, targets=None, cameras=None, target_points=None, image_points=None,
                 reference_camera='side', clockwise_rotation=True):
        """Instantiate a Calibration object with calibration data

        Args:
            angle_factor: start value for angle_factor. angle_factor is a float multiplier of rotation consign
                to obtain actual rotation angle (default value: 1)
            targets: a {target_id : CalibrationFrame,...} dict of targets to be used as starting guess for target frames
            cameras: a {camera_id: CalibrationCamera,...} dict of cameras to be used as starting guess for cameras
            target_points: a {target_id: [(x, y, z), ...], ...} dict of coordinates of target corner points, expressed
                in target corner point frame (chessboard frame)
            image_points: a {camera_id: {target_id : {rotation : [(u,v),...], ...}, ...,} dict of dict of dict of
                pixel coordinates of target corner points  projected on camera images at a given rotation consign. The
                rotation consign is the rounded angle (degrees) by which the turntable has turned before image acquisition
            reference_camera (str): camera_id of the camera to be used as reference for world frame (see details)
            clockwise_rotation (bool): are targets rotating clockwise ? (default True)

        Details:
            Calibration allows finding position and parameters of cameras and targets and compute the pixel coordinates
            any 3D point of world.
            The world 3D coordinates are expressed in world global frame, defined by the axis of rotation and a the
            position of a reference camera.
            The axis of rotation of the rotating system, oriented toward the sky, defines the world z-axis.
            The altitude of the reference camera defines the altitude of the world origin, and the reference camera
            z+-axis (camera optical axis) defines world Y+ axis
        """

        self.angle_factor = angle_factor
        self._targets = {}
        self._cameras = {}
        self._image_points = {}
        self._targets_points = {}
        self._nb_targets = 0
        self._nb_cameras = 0
        self._nb_image_points = 0

        self.set_values(targets, target_points, cameras, image_points)
        self.clockwise = clockwise_rotation
        self.reference_camera = reference_camera

        self.fit_angle_factor = True
        self.fit_reference_camera = True
        self.fit_targets = True
        self.fit_cameras = True
        self.verbose = False

    def set_values(self, targets=None, target_points=None, cameras=None, image_points=None):
        if targets is not None:
            self._targets = deepcopy(targets)
        if target_points is not None:
            self._targets_points = target_points
        if cameras is not None:
            self._cameras = deepcopy(cameras)
        if image_points is not None:
            self._image_points = image_points

        self._nb_cameras = len(self._cameras)
        self._nb_targets = len(self._targets)
        self._nb_image_points = 0
        for cam_pts in self._image_points.values():
            for im_pts_t in cam_pts.values():
                for im_pts in im_pts_t.values():
                    self._nb_image_points += len(im_pts)

    def __str__(self):
        out = 'Calibration:\n\n'

        out += 'Angle factor : ' + str(self.angle_factor) + '\n'
        out += 'Clockwise rotation : ' + str(self.clockwise) + '\n\n'

        for id_camera, camera in self._cameras.items():
            out += 'Camera {}'.format(id_camera)
            if id_camera == self.reference_camera:
                out += ' (reference)'
            out += ': \n'
            out += str(camera)

        for id_target, target in self._targets.items():
            out += 'Target {}: \n'.format(id_target)
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
        fr_cam = camera.get_frame()
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
            _pos_x = 0
            _pos_z = 0
            _focal_length_x, _focal_length_y, \
            _pos_y, \
            _rot_x, _rot_y, _rot_z = ref_cam
            ref_cam = [_focal_length_x, _focal_length_y,
                       _pos_x, _pos_y, _pos_z,
                       _rot_x, _rot_y, _rot_z]
            cameras.insert(0, ref_cam)

        # build frames
        angle_factor = self.angle_factor
        if len(turntable) > 0:
            angle_factor = turntable[0]

        target_frames = []
        if len(targets) > 0:
            for target in targets:
                pos_x, pos_y, pos_z, rot_x, rot_y, rot_z = target
                target_frames.append(CalibrationFrame.frame(pos_x, pos_y, pos_z, rot_x, rot_y, rot_z))
        else:
            for target in self._targets.values():
                target_frames.append(target.get_frame())

        camera_frames = []
        camera_focals = []
        for camera in cameras:
            _focal_length_x, _focal_length_y, \
            _pos_x, _pos_y, _pos_z, \
            _rot_x, _rot_y, _rot_z = camera
            camera_frames.append(CalibrationCamera.frame(_pos_x, _pos_y, _pos_z,
                                                         _rot_x, _rot_y, _rot_z))
            camera_focals.append([_focal_length_x, _focal_length_y])

        err = 0
        # cameras and image_points in the right order
        cams = []
        im_pts_cam = []
        if len(ref_cam) > 0:
            cams += [self._cameras[self.reference_camera]]
            im_pts_cam += [self._image_points[self.reference_camera]]
        cams += [self._cameras[k] for k in self._cameras if k is not self.reference_camera]
        im_pts_cam += [self._image_points[k] for k in self._cameras if k is not self.reference_camera]
        # target_points in the right order
        target_points = [self._targets_points[k] for k in self._targets]

        for fr_cam, focals, camera, im_pts_c in zip(camera_frames, camera_focals, cams, im_pts_cam):
            im_pts_t = [im_pts_c[k] for k in self._targets]
            for fr_target, t_pts, im_pts in zip(target_frames, target_points, im_pts_t):
                for rotation, ref_pts in im_pts.items():
                    fr_table = Calibration.turntable_frame(rotation, angle_factor, self.clockwise)
                    target_pts = fr_table.global_point(fr_target.global_point(t_pts))
                    _focal_length_x, _focal_length_y = focals
                    pts = CalibrationCamera.pixel_coordinates(fr_cam.local_point(target_pts),
                                                              camera._width_image,
                                                              camera._height_image,
                                                              _focal_length_x,
                                                              _focal_length_y)
                    err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self.verbose:
            print(err)

        return err

    def get_parameters(self):
        parameters = []
        if self.fit_angle_factor:
            parameters.append(self.angle_factor)
        if self.fit_reference_camera:
            c = self._cameras[self.reference_camera]
            parameters += [c._focal_length_x, c._focal_length_y,
                           c._pos_y,
                           c._rot_x, c._rot_y, c._rot_z]
        if self.fit_targets:
            for id_target,t in self._targets.items():
                parameters += [t._pos_x, t._pos_y, t._pos_z,
                               t._rot_x, t._rot_y, t._rot_z]
        if self.fit_cameras:
            for id_camera, c in self._cameras.items():
                if id_camera is not self.reference_camera:
                    parameters += [c._focal_length_x, c._focal_length_y,
                                   c._pos_x, c._pos_y, c._pos_z,
                                   c._rot_x, c._rot_y, c._rot_z]
        return parameters

    def find_parameters(self):

        start = self.get_parameters()
        parameters = scipy.optimize.minimize(
            self.fit_function,
            start,
            method='BFGS').x

        err = self.fit_function(parameters)

        if self.verbose:
            print('Result : ', parameters)
            print('Err : ', err / self._nb_image_points)

        return parameters

    def calibration_error(self):
        if self._nb_image_points > 0:
            p = self.get_parameters()
            return self.fit_function(p) / self._nb_image_points
        else:
            raise ValueError('Calibration corner points (target_points and image points) are required to compute '
                             'calibration error')

    def get_target_projected(self, id_camera, id_target, rotation):

        proj = self.get_projection(id_camera, rotation)
        target_pts = self.get_target_points(id_target)

        return proj(target_pts)

    def get_target_points(self, id_target):
        fr_target = self._targets[id_target].get_frame()
        return fr_target.global_point(self._targets_points[id_target])

    def calibrate(self, fit_angle_factor=True, fit_reference_camera=True, fit_targets=True, fit_cameras=True,
                  verbose=True):
        """Optimise the cameras and targets parameters to minimise the distance between
       observed image points and projections on images of target points

        Args:
            fit_angle_factor: should angle_factor be fitted ? (default True)
            fit_reference_camera: should reference camera parameters be fitted ? (default True)
            fit_targets: should target frame parameters be fitted ? (default True)
            fit_cameras: should other than reference camera parameters be fitted ? (default True)
            verbose: should total error be printed during optimisation (default True)

        Returns:
            the mean calibration reprojection error (pixels)
        """
        self.fit_angle_factor = fit_angle_factor
        self.fit_reference_camera = fit_reference_camera
        self.fit_targets = fit_targets
        self.fit_cameras = fit_cameras
        self.verbose = verbose

        parameters = self.find_parameters()

        turntable, ref_cam, target_pars, camera_pars = self.split_parameters(parameters)

        pos_labels = ['_pos_x', '_pos_y', '_pos_z']
        rot_labels = ['_rot_x', '_rot_y', '_rot_z']
        f_labels = ['_focal_length_x', '_focal_length_y']

        if len(turntable) > 0:
            self.angle_factor = turntable[0]

        if len(ref_cam) > 0:
            camera = self._cameras[self.reference_camera]
            labels = f_labels + ['_pos_y'] + rot_labels
            d = dict(zip(labels, ref_cam))
            for k in rot_labels:
                    d[k] = normalise_angle(d[k])
            camera.set_vars(d)

        if len(target_pars) > 0:
            labels = pos_labels + rot_labels
            for target, target_param in zip(self._targets.values(), target_pars):
                d = dict(zip(labels, target_param))
                for k in rot_labels:
                    d[k] = normalise_angle(d[k])
                target.set_vars(d)

        if len(camera_pars) > 0:
            cams = [self._cameras[k] for k in self._cameras if k is not self.reference_camera]
            for camera, camera_param in zip(cams, camera_pars):
                labels = f_labels + pos_labels + rot_labels
                d = dict(zip(labels, camera_param))
                for k in rot_labels:
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
        save_class['targets_parameters'] = {id_target: t.to_json() for id_target, t in self._targets.items()}

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
        c._cameras = {id_camera: CalibrationCamera.from_json(pars)
                      for id_camera, pars in save_class['cameras_parameters'].items()}
        c._targets = {id_target: CalibrationFrame.from_json(pars)
                      for id_target, pars in save_class['targets_parameters'].items()}
        c._nb_cameras = len(c._cameras)
        c._nb_targets = len(c._targets)
        c.angle_factor = save_class['angle_factor']
        c.clockwise = save_class['clockwise']
        c.reference_camera = save_class['reference_camera']
        return c


def load_old_calibration(side_file, top_file=None, chess_origin=(4 * 47, 3 * 47)):
    """Reader for old calibration

    Only a partly equivalent fit is provided (re-run calibrate will be necessary to optimise the parameters
    """
    cameras = {}
    targets = {}
    angle_factor = 1
    with open(side_file, 'r') as input_file:
        save_class = json.load(input_file)
        c = CalibrationCamera()
        c._width_image = save_class['cam_width_image']
        c._height_image = save_class['cam_height_image']
        c._focal_length_x = save_class['cam_focal_length_x']
        c._focal_length_y = save_class['cam_focal_length_y']
        c._pos_x = - save_class['cam_pos_x']
        c._pos_y = save_class['cam_pos_y']
        c._pos_z = save_class['cam_pos_z']
        # origin matrix for side cameras corresponds to -pi/2 rot around x axis
        rx = save_class['cam_rot_x'] - numpy.pi / 2.
        ry = save_class['cam_rot_y']
        rz = save_class['cam_rot_z']
        c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx), normalise_angle(ry), normalise_angle(rz)
        cameras['side'] = c
        angle_factor = save_class['angle_factor']

        for tn in ('target_1', 'target_2'):
            t = CalibrationFrame()
            t._pos_x = -save_class[tn + '_pos_x'] - chess_origin[0]
            t._pos_y = save_class[tn + '_pos_y'] - chess_origin[1]
            t._pos_z = save_class[tn + '_pos_z']
            # change of definition for rot
            t._rot_x = normalise_angle(save_class[tn + '_rot_x'] - save_class[tn + '_rot_y'])
            t._rot_y = 0
            t._rot_z = - normalise_angle(save_class[tn + '_rot_z'])
            targets[tn] = t

    if top_file is not None:
        with open(top_file, 'r') as input_file:
            save_class = json.load(input_file)
            c = CalibrationCamera()
            c._width_image = save_class['cam_width_image']
            c._height_image = save_class['cam_height_image']
            c._focal_length_x = save_class['cam_focal_length_x']
            c._focal_length_y = save_class['cam_focal_length_y']
            c._pos_x = - save_class['cam_pos_x']
            c._pos_y = save_class['cam_pos_y']
            c._pos_z = save_class['cam_pos_z']
            # origin matrix for top camera corresponds to pi rot around x axis and rot_z
            rx = save_class['cam_rot_x'] + numpy.pi
            ry = save_class['cam_rot_y']
            rz = save_class['cam_rot_z'] + numpy.pi / 2.
            c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx), normalise_angle(ry), normalise_angle(rz)
            cameras['top'] = c

    return Calibration(angle_factor=angle_factor, cameras=cameras, targets=targets, clockwise_rotation=True)


def find_position_3d_points(pt2d, calibrations):
    def fit_function(x0):

        sum_err = 0
        vec_err = list()
        for id_camera in pt2d:
            for angle in pt2d[id_camera]:
                if id_camera in calibrations:
                    calib = calibrations[id_camera]
                    fr_cam = calib.frame(calib._pos_x, calib._pos_y, calib._pos_z, calib._rot_x,
                                         calib._rot_y, calib._rot_z)

                    pos_x, pos_y, pos_z = x0
                    alpha = math.radians(angle * calib._angle_factor)

                    origin = [pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
                              pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
                              pos_z]

                    pt = calibrations[id_camera].pixel_coordinates(
                        fr_cam.local_point(origin),
                        calib._width_image,
                        calib._height_image,
                        calib._focal_length_x,
                        calib._focal_length_y)

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
                        fr_cam = calib.frame(calib._pos_x, calib._pos_y, calib._pos_z,
                                             calib._rot_x, calib._rot_y, calib._rot_z)

                        pos_x, pos_y, pos_z = sf.global_point(
                            (x0[4 + i * 2], x0[5 + i * 2], 0))
                        alpha = math.radians(angle * calib._angle_factor)

                        origin = [pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
                                  pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
                                  pos_z]

                        pt = calib.pixel_coordinates(
                            fr_cam.local_point(origin),
                            calib._width_image,
                            calib._height_image,
                            calib._focal_length_x,
                            calib._focal_length_y)

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


class OldCalibrationCamera(object):
    """A class for using camera calibrated with older version of phenomenal (< 1.7.1)"""
    def __init__(self):
        # Camera Parameters
        self._cam_width_image = None
        self._cam_height_image = None
        self._cam_focal_length_x = None
        self._cam_focal_length_y = None
        self._cam_pos_x = None
        self._cam_pos_y = None
        self._cam_pos_z = None
        self._cam_rot_x = None
        self._cam_rot_y = None
        self._cam_rot_z = None
        self._angle_factor = None
        self._cam_origin_axis = None

    def __str__(self):
        out = ''
        out += 'Camera Parameters : \n'
        out += '\tFocal length X : ' + str(self._cam_focal_length_x) + '\n'
        out += '\tFocal length Y : ' + str(self._cam_focal_length_y) + '\n'
        out += '\tOptical Center X : ' + str(self._cam_width_image / 2.0) + '\n'
        out += '\tOptical Center Y : ' + str(self._cam_height_image / 2.0)
        out += '\n\n'

        out += '\tPosition X : ' + str(self._cam_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._cam_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._cam_pos_z) + '\n\n'

        out += '\tRotation X : ' + str(self._cam_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._cam_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._cam_rot_z) + '\n'

        out += '\t Angle Factor : ' + str(self._angle_factor) + '\n'

        out += '\tOrigin rotation position : \n'
        out += str(self._cam_origin_axis) + '\n\n'

        return out

    @staticmethod
    def pixel_coordinates(point_3d,
                          width_image, height_image,
                          focal_length_x, focal_length_y):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
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


    @staticmethod
    def pixel_coordinates_2(point_3d, cx, cy, fx, fy):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        # if point[2] < 1:
        #     raise UserWarning("point too close to the camera")

        u = point_3d[0] / point_3d[2] * fx + cx
        v = point_3d[1] / point_3d[2] * fy + cy

        return u, v

    @staticmethod
    def target_frame(pos_x, pos_y, pos_z,
                     rot_x, rot_y, rot_z,
                     alpha):

        origin = [
            pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
            pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
            pos_z]

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(alpha + rot_z, z_axis)

        rot = concatenate_matrices(mat_rot_z, mat_rot_x, mat_rot_y)

        return Frame(rot[:3, :3].T, origin)

    @staticmethod
    def camera_frame(pos_x, pos_y, pos_z,
                     rot_x, rot_y, rot_z,
                     origin_axis):

        origin = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        rot = concatenate_matrices(origin_axis,
                                   mat_rot_x, mat_rot_y, mat_rot_z)

        return Frame(rot[:3, :3].T, origin)

    def get_camera_frame(self):
        return self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

    def get_projection(self, alpha):

        fr_cam = self.get_camera_frame()

        angle = math.radians(alpha * self._angle_factor)

        def projection(pts):
            pts = numpy.array(pts)
            x = - pts[:, 0] * math.cos(angle) - pts[:, 1] * math.sin(angle)
            y = - pts[:, 0] * math.sin(angle) + pts[:, 1] * math.cos(angle)
            z = pts[:, 2]

            origin = numpy.column_stack((x, y, z))

            return self.pixel_coordinates(fr_cam.local_point(origin),
                                              self._cam_width_image,
                                              self._cam_height_image,
                                              self._cam_focal_length_x,
                                              self._cam_focal_length_y)

        return projection

    def get_projection2(self, alpha):
        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        angle = math.radians(alpha * self._angle_factor)

        def projection(pt):
            # -pt[0] = x <=> For inverse X axis orientation
            origin = [pt[0] * math.cos(angle) - pt[1] * math.sin(angle),
                      pt[0] * math.sin(angle) + pt[1] * math.cos(angle),
                      pt[2]]

            return self.pixel_coordinates(fr_cam.local_point(origin),
                                          self._cam_width_image,
                                          self._cam_height_image,
                                          self._cam_focal_length_x,
                                          self._cam_focal_length_y)

        return projection

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

        c = OldCalibrationCamera()
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
        if 'target_1_pos_x' in save_class:
            c._target_1_pos_x = save_class['target_1_pos_x']
            c._target_1_pos_y = save_class['target_1_pos_y']
            c._target_1_pos_z = save_class['target_1_pos_z']
            c._target_1_rot_x = save_class['target_1_rot_x']
            c._target_1_rot_y = save_class['target_1_rot_y']
            c._target_1_rot_z = save_class['target_1_rot_z']
        if 'target_2_pos_x' in save_class:
            c._target_2_pos_x = save_class['target_2_pos_x']
            c._target_2_pos_y = save_class['target_2_pos_y']
            c._target_2_pos_z = save_class['target_2_pos_z']
            c._target_2_rot_x = save_class['target_2_rot_x']
            c._target_2_rot_y = save_class['target_2_rot_y']
            c._target_2_rot_z = save_class['target_2_rot_z']


        return c

    def dump(self, filename):
        save_class = dict()

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
        save_class['angle_factor'] = self._angle_factor
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16, )).tolist()

        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
