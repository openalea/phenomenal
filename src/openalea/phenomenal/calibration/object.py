from __future__ import division, absolute_import, print_function

import json
import math

import numpy

from .transformations import rotation_matrix, concatenate_matrices
from .frame import Frame, x_axis, y_axis, z_axis


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
    def from_tuple(pars):
        cf = CalibrationFrame()
        cf._pos_x, cf._pos_y, cf._pos_z, cf._rot_x, cf._rot_y, cf._rot_z = pars
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

    The camera is a perfect pinhole camera associated to a calibrationframe allowing its positioning in space.

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
        self._aspect_ratio = None

    def __str__(self):
        out = ''
        fmm = numpy.round(self._focal_length_x / max(self._width_image, self._height_image) * 36)
        out += '\tFocal length X : ' + str(self._focal_length_x) + ' (' + str(fmm) + 'mm)\n'
        out += '\tPixel aspect ratio : ' + str(self._aspect_ratio) + '\n'
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
                          focal_length_x, aspect_ratio):
        """ Compute image coordinates of a 3d point positioned in camera frame

        Args:
         - point (float, float, float): a point/array of points in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        pt = numpy.array(point_3d)
        x, y, z = pt.T
        focal_length_y = aspect_ratio * focal_length_x

        u = x / z * focal_length_x + width_image / 2.0
        v = y / z * focal_length_y + height_image / 2.0

        if len(pt.shape) > 1:
            return numpy.column_stack((u, v))
        else:
            return u, v

    def get_pixel_coordinates(self):
        def pixel_coords(pts):
            return self.pixel_coordinates(pts, self._width_image, self._height_image,
                                          self._focal_length_x, self._aspect_ratio)
        return pixel_coords

    @staticmethod
    def pixel_coordinates_2(point_3d, cx, cy, fx, a):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        pt = numpy.array(point_3d)
        x, y, z = pt.T
        fy = a * fx

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

    def image_shape(self):
        return self._height_image, self._width_image

    def get_intrinsic(self):
        intrinsic = numpy.identity(3)
        fx = self._focal_length_x
        fy = self._focal_length_x * self._aspect_ratio
        cx = self._width_image / 2.
        cy = self._height_image / 2.
        di = numpy.diag_indices(2)
        intrinsic[:2, 2] = (cx, cy)
        intrinsic[di] = (fx, fy)
        return intrinsic

    @staticmethod
    def from_json(save_class):
        c = CalibrationCamera()
        if '_focal_length_y' in save_class:
            fy = save_class.pop('_focal_length_y')
            save_class['_aspect_ratio'] = fy / save_class['_focal_length_x']
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
