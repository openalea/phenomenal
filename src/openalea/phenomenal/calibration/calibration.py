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
           "OldCalibration"]


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

class CalibrationLayout(object):
    """Helper for defining the calibration layout for a rotating multiview acquisition system"""

    def __init__(self, reference_camera = None, cameras=None, targets=None, clockwise_rotation=True):
        """

        Args:
            reference_camera:  a (distance, inclination) tuple defining the reference camera. The camera is positioned
                relative to a camera placed on the axis of rotation (world Z+) at an arbitrary position defining world origin  and pointing downward. Distance
                isInclination
                is the angle (degree, positive) needed to position the
            cameras:
            targets:
            clockwise_rotation:
        """
        pass

class CalibrationSetup(object):
    """A class for helping the setup of a multi-view imaging systems to be calibrated"""

    def __init__(self, cameras=None, targets=None, image_resolutions=None, image_sizes=None, facings=None,
                 clockwise_rotation=True):
        """ Instantiate a CalibrationSetup for positioning cameras and targets of a multiview acquisition system

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
                 reference_camera='side', clockwise_rotation=True, calibration_statistics=None):
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
            calibration_statistics (dict): statitistics of current calibration

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

        self.calibration_statistics = calibration_statistics

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

    def calibration_error(self, all_pars=False):
        if self._nb_image_points > 0:
            before = {}
            if all_pars:
                before['fit_angle_factor'] = self.fit_angle_factor
                before['fit_reference_camera'] = self.fit_reference_camera
                before['fit_targets'] = self.fit_targets
                before['fit_cameras'] = self.fit_cameras
                self.fit_angle_factor = True
                self.fit_reference_camera = True
                self.fit_targets = True
                self.fit_cameras = True

            p = self.get_parameters()
            err = self.fit_function(p)

            if all_pars:
                self.fit_angle_factor = before['fit_angle_factor']
                self.fit_reference_camera = before['fit_reference_camera']
                self.fit_targets = before['fit_targets']
                self.fit_cameras = before['fit_cameras']

            return err, err / self._nb_image_points
        else:
            raise ValueError('Calibration corner points (target_points and image points) are required to compute '
                             'calibration error')

    def _calibration_statistics(self):
        stats = {}
        if self._nb_image_points > 0:
            _, error = self.calibration_error(all_pars=True)
            stats['mean_error'] = error
            stats['total_points'] = self._nb_image_points
        for id_camera, camera in self._cameras.items():
            d_origin = numpy.sqrt(camera._pos_x ** 2 + camera._pos_y ** 2 + camera._pos_z ** 2)
            focal = numpy.mean([camera._focal_length_x,
                                camera._focal_length_y])
            pixel_size = d_origin / focal
            calibration_images = {}
            if self._nb_image_points > 0:
                for target in self._image_points[id_camera]:
                    calibration_images[target] = len(self._image_points[id_camera][target])
            stats[id_camera] = {'distance to origin': d_origin,
                                'pixel_size': pixel_size,
                                'target_images': calibration_images}
        return stats

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
            d = dict(list(zip(labels, ref_cam)))
            for k in rot_labels:
                    d[k] = normalise_angle(d[k])
            camera.set_vars(d)

        if len(target_pars) > 0:
            labels = pos_labels + rot_labels
            for target, target_param in zip(self._targets.values(), target_pars):
                d = dict(list(zip(labels, target_param)))
                for k in rot_labels:
                    d[k] = normalise_angle(d[k])
                target.set_vars(d)

        if len(camera_pars) > 0:
            cams = [self._cameras[k] for k in self._cameras if k is not self.reference_camera]
            for camera, camera_param in zip(cams, camera_pars):
                labels = f_labels + pos_labels + rot_labels
                d = dict(list(zip(labels, camera_param)))
                for k in rot_labels:
                    d[k] = normalise_angle(d[k])
                camera.set_vars(d)

        err = self.fit_function(parameters)
        self.calibration_statistics = self._calibration_statistics()

        return err / self._nb_image_points

    def find_points(self, image_points, start=None, niter=100):
        """ Find 3D world coordinates of points from paired image coordinates on multiple cameras

        Args:
            image_points: a {camera_id: [(u1,v1),...], ...} dict of list of pixel coordinates of remarkable points
            taken on several images
            start (optional): a array-like list of 3D points guesses
            niter: (int) the number of iteration of the basin-hopping optimisation algorithm

        Returns:
            An array of 3D coordinates of points

        """

        image_points = {k: numpy.array(v) for k, v in image_points.items()}
        if start is None:
            start = numpy.array([(0, 0, 0)] * len(image_points.values()[0]))

        def fit_function(x0):
            err = 0
            pts = numpy.array(x0).reshape((int(len(x0) / 3), 3))
            for id_camera in image_points:
                im_pts = image_points[id_camera]
                proj = self.get_projection(id_camera, 0)
                pix = proj(pts)
                err += numpy.linalg.norm(pix - im_pts, axis=1).sum()
            print(err)
            return err

        parameters = scipy.optimize.minimize(
            fit_function,
            start,
            method='BFGS').x
        print("Err : ", fit_function(parameters))

        return parameters.reshape((int(len(parameters) / 3), 3))

    def find_camera(self, image_points, target_points, image_size, fixed_parameters=None, guess=None,  niter=10):
        """ Find camera parameters from clicked image points of known 3D target points

        Args:
            image_points: an array-like list of image coordinates of remarkable points
            target_points: an array-like list of 3D coordinates of remarkable points
            image_size: (width, height) tuple describing image dimension (pixels)
            fixed_parameters: a {parameter_name: value} dict of fixed (unfitted) camera parameters. Valid parameters
             names are '_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z', '_focal_length_x', '_focal_length_y'
            guess : a guessed Calibration camera
            niter: (int) the number of iteration of the basin-hopping optimisation algorithm

        Returns:
            A calibrated CalibrationCamera
        """

        image_points = numpy.array(image_points)
        target_points = numpy.array(target_points)

        if fixed_parameters is None:
            fixed_parameters = {}
        w, h = image_size
        fixed_parameters.update({'_width_image': w, '_height_image': h})

        pars = ('_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z', '_width_image', '_height_image',
                '_focal_length_x', '_focal_length_y')
        free_pars = [p for p in pars if p not in fixed_parameters]
        nfree_pars = len(free_pars)

        if guess is None:
            start = numpy.zeros(nfree_pars)
        else:
            d = vars(guess)
            start = [d[p] for p in free_pars]

        def split_parameters(x0):
            pars = dict(list(zip(free_pars, x0[:nfree_pars])))
            pars.update(fixed_parameters)
            return pars

        def fit_function(x0):
            pars = split_parameters(x0)
            camera = CalibrationCamera()
            camera.set_vars(pars)
            proj = camera.get_projection()
            pix = proj(target_points)
            err = numpy.linalg.norm(pix - image_points, axis=1).sum()
            print(err)
            return err

        parameters = scipy.optimize.minimize(
            fit_function,
            start,
            method='BFGS').x

        pars = split_parameters(parameters)
        for p in ('_rot_x', '_rot_y', '_rot_z'):
            pars[p] = normalise_angle(pars[p])
        camera = CalibrationCamera()
        camera.set_vars(pars)

        return camera

    def find_frame(self, image_points, fixed_parameters=None, fixed_frame_points=None, fixed_coords=None):
        """ Find Frame parameters and 3D local (frame based) coordinates of points from paired image coordinates

        Args:
            image_points: a {camera_id: [(u1,v1),...], ...} dict of list of pixel coordinates of frame points
            fixed_parameters: a {parameter_name: value} dict of fixed (unfitted) frame parameters. Valid parameters
             names are '_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z'
            fixed_frame_points: an array-like list of 3D points coordinates, expressed in the local frame coordinate
            system. If None (default), frame points are fitted from image_points coordinates.
            fixed_coords: a {axis: value} dict specifying fixed local coordinates of points, if any. Valid
             keys are 'x', 'y', or 'z'

        Returns:
            A calibrated CalibrationFrame and a list of 3D coordinates of points, expressed in the frame
             coordinate system

        """

        if fixed_parameters is None:
            fixed_parameters = {}

        if fixed_coords is None:
            fixed_coords = {}

        image_points = {k: numpy.array(v) if v is not None else v for k, v in image_points.items()}
        n_pts = len(list(image_points.values())[0])

        for c in fixed_coords:
            fixed_coords[c] = [fixed_coords[c]] * n_pts

        # free frame parameters
        pars = ('_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z')
        free_pars = [p for p in pars if p not in fixed_parameters]
        nfree_pars = len(free_pars)

        # free (unknown) points
        nfree_pts = n_pts
        if fixed_frame_points is not None:
            nfree_pts -= len(fixed_frame_points)
            fixed_frame_points = [numpy.array(v) for v in fixed_frame_points]
        else:
            fixed_frame_points = []

        # free point coordinates
        coords = ('x', 'y', 'z')
        free_coords = [c for c in coords if c not in fixed_coords]
        nfree_coords = len(free_coords)

        def split_parameters(x0):
            pars = dict(list(zip(free_pars, x0[:nfree_pars])))
            pars.update(fixed_parameters)

            fpts = fixed_frame_points
            if nfree_pts > 0:
                pts = numpy.array(x0[nfree_pars:]).reshape((nfree_pts, nfree_coords))
                coords = dict(list(zip(free_coords, zip(*pts))))
                coords.update(fixed_coords)
                fpts += list(zip(coords['x'], coords['y'], coords['z']))

            return pars, fpts

        def fit_function(x0):
            pars, fpts = split_parameters(x0)
            cframe = CalibrationFrame()
            cframe.set_vars(pars)
            fr = cframe.get_frame()
            pts = fr.global_point(fpts)

            err = 0
            for id_camera in image_points:
                im_pts = [p for p in image_points[id_camera] if p is not None]
                world_pts = [p for p, im_p in zip(pts, image_points[id_camera]) if im_p is not None ]
                proj = self.get_projection(id_camera, 0)
                pix = proj(world_pts)
                err += numpy.linalg.norm(pix - im_pts, axis=1).sum()
            print(err)

            return err

        start = numpy.zeros(nfree_pars + nfree_pts * nfree_coords)
        parameters = scipy.optimize.minimize(
            fit_function,
            start,
            method='BFGS').x

        pars, fpts = split_parameters(parameters)
        for p in ('_rot_x', '_rot_y', '_rot_z'):
            pars[p] = normalise_angle(pars[p])
        cframe = CalibrationFrame()
        cframe.set_vars(pars)

        return cframe, fpts

    def find_frame_from_vectors(self, image_vectors, world_vectors, fixed_parameters=None):
        """ Find Frame parameters from magnitude and orientation of known vectors / projected vectors pairs

        Args:
            image_vectors: a {camera_id: [(magnitude, orientation),...], ...} dict of list of projeted vectors in image frame.
                           Orientation is the angle between image width direction and projected vector, positive counterclockwise
            world_vectors : a [(magnitude, elevation, azimuth),...] list of vectors in world frame
            fixed_parameters: a {parameter_name: value} dict of fixed (unfitted) frame parameters. Valid parameters
             names are '_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z'


        Returns:
            A CalibrationFrame

        """

        if fixed_parameters is None:
            fixed_parameters = {}

        # u = x, v = -y if angle are counterclockwise
        image_points = {k: numpy.array([(m * numpy.cos(t), -m * numpy.sin(t)) for m, t in v]) for k, v in image_vectors.items()}

        fpts = numpy.array(
            [(m * numpy.cos(el) * numpy.cos(az), m * numpy.cos(el) * numpy.sin(az),m * numpy.sin(el)) for m, el, az in
             world_vectors])

        # free frame parameters
        pars = ('_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z')
        free_pars = [p for p in pars if p not in fixed_parameters]
        nfree_pars = len(free_pars)

        def split_parameters(x0):
            pars = dict(list(zip(free_pars, x0)))
            pars.update(fixed_parameters)
            return pars

        def fit_function(x0):
            pars = split_parameters(x0)
            cframe = CalibrationFrame()
            cframe.set_vars(pars)
            fr = cframe.get_frame()
            pts = fr.global_point(fpts)

            err = 0
            for id_camera in image_points:
                proj = self.get_projection(id_camera, 0)
                im_pts = proj(fr.global_point((0, 0, 0))) + image_points[id_camera]
                pix = proj(pts)
                err += numpy.linalg.norm(pix - im_pts, axis=1).sum()
            print(err)

            return err

        start = numpy.zeros(nfree_pars)
        parameters = scipy.optimize.minimize(
            fit_function,
            start,
            method='BFGS').x

        pars = split_parameters(parameters)
        for p in ('_rot_x', '_rot_y', '_rot_z'):
            pars[p] = normalise_angle(pars[p])
        cframe = CalibrationFrame()
        cframe.set_vars(pars)

        return cframe

    def dump(self, filename):
        save_class = dict()
        save_class['angle_factor'] = self.angle_factor
        save_class['clockwise'] = self.clockwise
        save_class['reference_camera'] = self.reference_camera
        save_class['cameras_parameters'] = {id_camera: camera.to_json() for id_camera, camera in self._cameras.items()}
        save_class['targets_parameters'] = {id_target: t.to_json() for id_target, t in self._targets.items()}

        if self.calibration_statistics is not None:
            save_class['calibration_statistics'] = self.calibration_statistics

        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def from_dict(save_class):
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
        if 'calibration_statistics' in save_class:
            c.calibration_statistics = save_class['calibration_statistics']
        return c

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)
        return Calibration.from_dict(save_class)


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

    def get_pixel_coordinates(self):
        def pixel_coords(pts):
            return self.pixel_coordinates(pts, self._cam_width_image, self._cam_height_image,
                                          self._cam_focal_length_x, self._cam_focal_length_y)
        return pixel_coords

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


class OldCalibration(object):
    """A class for loading, inspecting and convert old Calibration to new Calibration"""

    def __init__(self, cameras, targets):
        """ Instantiate an OldCalibration instance

        Args:
            cameras: a {id_camera: OldCalibrationCamera, ...} dict of calibrated cameras objects (see
            OldCameraCalibration class)
            chessboards: a {id_target: Chessboard, ...} dict of Chessboard objects (see Chessboard class in
            chessboard.py)
        """
        self.cameras = cameras
        self.targets = targets

    def calibration_error(self):
        """error (pixels) between detected target image points and reprojection of 3D target points"""

        image_points = {camera: {k: v.get_corners_2d(camera) for k, v in self.targets.items()} for camera in
                        self.cameras}
        target_points = {k: v.get_corners_local_3d(old_style=True) for k, v in self.targets.items()}

        err = 0
        nb_pts = 0
        target_parameters = vars(self.cameras['side'])
        for camera in image_points:
            for target in image_points[camera]:
                for angle in image_points[camera][target]:
                    cam = self.cameras[camera]
                    pars = [target_parameters['_' + target + '_' + x] for x in ('pos_x', 'pos_y', 'pos_z',
                                                                                'rot_x', 'rot_y', 'rot_z')]
                    pars += [numpy.radians(cam._angle_factor * angle)]
                    fr_target = cam.target_frame(*pars)
                    fr_cam = cam.get_camera_frame()
                    pix_coord = cam.get_pixel_coordinates()
                    pts_ref = image_points[camera][target][angle]
                    pts = pix_coord(fr_cam.local_point(fr_target.global_point(target_points[target])))
                    nb_pts += len(pts)
                    err += numpy.linalg.norm(pts - pts_ref, axis=1).sum()

        return err, float(err) / nb_pts

    def guess_new_calibration(self):
        """Instantiate a Calibration object using fitted parameters

        Returns:
            An (unfitted) Calibration object
        """
        cameras = {}
        targets = {}
        #
        angle_factor = self.cameras['side']._angle_factor
        tpars = vars(self.cameras['side'])
        for tn, target in self.targets.items():
            w, h = target.shape
            size = target.square_size
            chess_origin = ((w / 2.) * size, (h / 2.) * size)

            t = CalibrationFrame()
            t._pos_x = -tpars['_' + tn + '_pos_x'] - chess_origin[0]
            t._pos_y = tpars['_' + tn + '_pos_y'] - chess_origin[1]
            t._pos_z = tpars['_' + tn + '_pos_z']
            # change of definition for rot
            t._rot_x = normalise_angle(tpars['_' + tn + '_rot_x'] - tpars['_' + tn + '_rot_y'])
            t._rot_y = 0
            t._rot_z = - normalise_angle(tpars['_' + tn + '_rot_z'])
            targets[tn] = t

        for cn, camera in self.cameras.items():
            c = CalibrationCamera()
            c._width_image = camera._cam_width_image
            c._height_image = camera._cam_height_image
            c._focal_length_x = camera._cam_focal_length_x
            c._focal_length_y = camera._cam_focal_length_y
            c._pos_x = - camera._cam_pos_x
            c._pos_y = camera._cam_pos_y
            c._pos_z = camera._cam_pos_z
            if cn == 'side':
                # origin matrix for side cameras corresponds to -pi/2 rot around x axis
                rx = camera._cam_rot_x - numpy.pi / 2.
                ry = camera._cam_rot_y
                rz = camera._cam_rot_z
            else:
                rx = camera._cam_rot_x + numpy.pi
                ry = camera._cam_rot_y
                rz = camera._cam_rot_z + numpy.pi / 2.
            c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx), normalise_angle(ry), normalise_angle(rz)
            cameras[cn] = c

        return Calibration(angle_factor=angle_factor, cameras=cameras, targets=targets,
                           clockwise_rotation=True, reference_camera='side')


# deprecated functions used in old calibration scripts (see equivalents in Calibration methods)

def find_position_3d_points(pt2d, calibration):
    """ Find the coordinates of one point clicked on several image

    Args:
        pt2d: a {id_camera:{angle:(x, y),...},...} dict of pixel coordinates
        calibration: a calibrated Calibration object

    Returns:

    """
    image_points = {id_cam: [pt2d[0]] for id_cam in pt2d}
    return calibration.find_points(image_points)



def find_position_3d_points_soil(im_pts, calibration):
    image_points = {id_cam: [im_pts[0]] for id_cam in im_pts}
    return calibration.find_frame(image_points, fixed_parameters={'_pos_x': 0, '_pos_y': 0}, fixed_coords={'z': 0})

