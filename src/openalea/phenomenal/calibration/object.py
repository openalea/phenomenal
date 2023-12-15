from __future__ import division, absolute_import, print_function

import warnings
import json
import math
from copy import deepcopy
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

    @property
    def distance_to_origin(self):
        return numpy.sqrt(self._pos_x ** 2 + self._pos_y ** 2 + self._pos_z ** 2)

    @property
    def pixel_size_at_origin(self):
        """size of pixel (world unit) at world origin"""
        focal = self._focal_length_x * (1 + self._aspect_ratio) / 2
        return self.distance_to_origin / focal

    def __str__(self):
        out = ''
        fmm = numpy.round(self._focal_length_x / max(self._width_image, self._height_image) * 36)
        out += '\tFocal length X : ' + str(self._focal_length_x) + ' (' + str(fmm) + 'mm)\n'
        out += '\tPixel aspect ratio : ' + str(self._aspect_ratio) + '\n'
        out += '\tPixel size at origin : ' + str(self.pixel_size_at_origin) + '\n'
        out += '\tdistance to origin : ' + str(self.pixel_size_at_origin) + '\n'
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


class Calibration(object):
    """A class for calibrated rotation system"""
    def __init__(self,angle_factor=1, targets=None, cameras=None, target_points=None,
                 reference_camera='side', clockwise_rotation=True, calibration_statistics=None, frames=None):
        self.angle_factor = angle_factor
        self._targets = {}
        self._targets_points = {}
        self._cameras = {}
        if cameras is not None:
            self._cameras = deepcopy(cameras)
        if targets is not None:
            self._targets = deepcopy(targets)
        if target_points is not None:
            self._targets_points = target_points
        self.clockwise = clockwise_rotation
        self.reference_camera = reference_camera

        self.calibration_statistics = calibration_statistics
        if frames is not None:
            self.frames = frames
        else:
            self.frames = {}

    @property
    def _nb_targets(self):
        return len(self._targets)
    @property
    def _nb_cameras(self):
        return len(self._cameras)

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

    def dump(self, filename):
        save_class = dict()
        save_class['angle_factor'] = self.angle_factor
        save_class['clockwise'] = self.clockwise
        save_class['reference_camera'] = self.reference_camera
        save_class['cameras_parameters'] = {id_camera: camera.to_json() for id_camera, camera in self._cameras.items()}
        save_class['targets_parameters'] = {id_target: t.to_json() for id_target, t in self._targets.items()}

        if self.calibration_statistics is not None:
            save_class['calibration_statistics'] = self.calibration_statistics

        if len(self.frames) > 0:
            save_class['frames'] = {id_frame: frame.to_json() for id_frame, frame in self.frames.items()}

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
        c.angle_factor = save_class['angle_factor']
        c.clockwise = save_class['clockwise']
        c.reference_camera = save_class['reference_camera']
        if 'calibration_statistics' in save_class:
            c.calibration_statistics = save_class['calibration_statistics']
        if 'frames' in save_class:
            c.frames = {id_frame: CalibrationFrame.from_json(pars)
                             for id_frame, pars in save_class['frames'].items()}
        return c

    @staticmethod
    def load(filename):
        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)
        return Calibration.from_dict(save_class)


    def get_frame(self, frame='native'):

        if frame == 'native':
            return Frame()
        elif frame in self.frames:
            return self.frames[frame].get_frame()
        else:
            warnings.warn('frame: ' + frame + ' not defined, falling back to native world frame')
            return Frame()


    @staticmethod
    def turntable_frame(rotation, angle_factor=1, clockwise=True):
        """ Frame attached to turntable. This correspond to a rotation of the world native frame.

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


    def get_projection(self, id_camera, rotation, world_frame='native'):

        camera = self._cameras[id_camera]
        fr_cam = camera.get_frame()
        fr_table = self.get_turntable_frame(rotation)
        fr_world = self.get_frame(world_frame)

        pixel_coords = camera.get_pixel_coordinates()

        def projection(pts):
            # native points
            npts = fr_world.global_point(pts)
            # rotated pts
            rotated = fr_table.global_point(npts)
            return pixel_coords(fr_cam.local_point(rotated))

        return projection

    def get_image_shape(self, id_camera):
        return self._cameras[id_camera].image_shape()

    def world_frame(self, camera):
        """World frame defined by an alternative camera positioned in the current reference camera world frame"""
        ref_azim = -numpy.pi / 2 # by definition of the reference camera
        azim = numpy.arctan2(camera._pos_y, camera._pos_x)
        return CalibrationFrame.from_tuple((0, 0, camera._pos_z, 0, 0, azim - ref_azim))

    def frame_lines(self, view, angle, frame='native', l=100, w=10, at = (0, 0, 0)):
        base_axis = numpy.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        p = self.get_projection(view, angle, frame)
        origin = tuple(numpy.array(p(at)).astype(int))
        lines = []
        for axe in base_axis:
            end = tuple(numpy.array(p(numpy.array(at) + l * axe)).astype(int))
            col = tuple([int(x) for x in axe * 255])
            lines.append((origin, end, col, w))
        return lines

    def get_target_points(self, id_target):
        if id_target == 'world':
            fr_target = self.get_frame('native')
        else:
            fr_target = self._targets[id_target].get_frame()
        return fr_target.global_point(self._targets_points[id_target])

    def get_target_projected(self, id_camera, id_target, rotation):
        proj = self.get_projection(id_camera, rotation)
        target_pts = self.get_target_points(id_target)

        return proj(target_pts)

    def target_mask(self, id_camera, id_target, rotation, border=2):
        """Get image coordinate of a mask arround the target

            Args:
                border : the size of the border (in square_size units)
        """
        pts = self.get_target_projected(id_camera, id_target, rotation)
        targ = self._targets[id_target]
        bs = targ.square_size * border / self._cameras[id_camera].pixel_size_at_origin
        proj = self.get_projection(id_camera, rotation)
        pts = self._targets[id_target]
        u, v = zip(*pts)
        h,w = self._cameras[id_camera].image_shape()
        umin, vmin, umax, vmax = (numpy.clip(min(u) - bs, 1, w),
                                  numpy.clip(min(v) - bs, 1, h),
                                  numpy.clip(max(u) + bs, 1, w),
                                  numpy.clip(max(v) + bs, 1, h))
        return [(umin,vmin), (umax, vmin), (umax, vmax), (umin, vmax)]




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



# reader for old calibration
def normalise_angle(angle):
    """normalise an angle to the [-pi, pi] range"""
    angle = numpy.array(float(angle))
    modulo = 2 * numpy.pi
    angle %= modulo
    # force to [0, modulo] range
    angle = (angle + modulo) % modulo
    return angle - numpy.where(angle > modulo / 2., modulo, 0)
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