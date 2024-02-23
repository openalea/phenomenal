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



import numpy
import scipy.optimize
import cv2
import os
from itertools import islice
from copy import deepcopy
from collections import defaultdict


from .object import CalibrationFrame, CalibrationCamera, Calibration
from .chessboard import (Chessboard)

# ==============================================================================

__all__ = ["Calibrator",
           "CalibrationSetup",
           "CalibrationSolver"]


# ==============================================================================


def normalise_angle(angle):
    """normalise an angle to the [-pi, pi] range"""
    angle = numpy.array(float(angle))
    modulo = 2 * numpy.pi
    angle %= modulo
    # force to [0, modulo] range
    angle = (angle + modulo) % modulo
    return angle - numpy.where(angle > modulo / 2., modulo, 0)

def angle3(v1, v2):
    """acute angle between 2 3d vectors"""
    x = numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))
    angle = numpy.arccos(numpy.clip(x, -1, 1))
    return numpy.degrees(angle)


class Calibrator(object):
    """Class for end to end calibration of rotating multiview acquisition system"""

    def __init__(self, south_camera, cameras=None, targets=None, chessboards=None,
                 image_paths=None, clockwise_rotation=True, world_unit='mm', data_dir='.', calibration_dir='./Calibration'):
        """
        Setup Calibrator with the calibration layout

        Args:
            south_camera:  a (camera_id, inclination, distance) tuple defining the approximative position of the south camera.
                The south camera is used to define world frame during and after calibration (see details bellow).
                camera_id is a string referencing the camera, inclination is the (approximative) angle (degree, positive)
                between the axis of rotation and the axe passing through the turntable center and camera optical center,
                and distance is the (approximative) distance from turntable center to camera optical center (in world units).
            cameras: a {camera_id: (inclination, distance, rotation_to_south), ... } dict of 3-tuples specifying the
                approximative position of cameras (other than south camera). camera_id is a string referencing the camera,
                inclination is the (approximative) angle (degree, positive) between the axis of rotation and the axe
                passing through the turntable center and camera optical center, distance is the (approximative) distance
                from turntable center to camera optical center (in world units), and rotation_to_south is the (approximative)
                rotation angle (degrees, positive in the direction of rotation of the turntable) that align the camera
                to south.
            targets: a {target_id: (inclination, rotation_to_south), ...} dict of 2-tuples specifying the
                approximative position of calibration targets. target_id is a string referencing the target, inclination
                is the angle (degree, positive) between the axis of rotation and target normal, and rotation_to_south is
                the (approximative) rotation angle (degrees, positive in the direction of rotation of the turntable that
                align the target normal(or target base) toward south.
            chessboards: a {target_id: (between_corners, corners_h, corners_v), ...} dict of tuples describing the layout
                of chessboards corner points (intersections of cheesboard squares) associated to a target. target_id is
                a string referencing the target, between_corners is the distance (in world unit) between two corner
                points, corners_h is the number of corners in the horizontal direction, corners_v in the number of
                corners in the vertical direction.
            image_paths: a {camera_id : {rotation_angle : path, ...},...} nested dict of image paths
                pointing to the image camera 'camera_id' after a rotation of 'rotation_angle'
                degrees of the turntable. Path are relative to data_dir or absolute paths if data_dir is None
            clockwise_rotation: (bool): is the turntable rotating clockwise ? (default True)
            world_unit (str): a label describing world units
            data_dir: the path of the directory containing images
            calibration_dir: the path of the directory to be used for calibration outputs

        Details:
            The world 3D coordinates are expressed in a 'native' frame defined by the axis of rotation and the south
            camera as follow:
                - The axis of rotation of the rotating system, oriented toward the sky, defines the world  Z+.
                - The altitude of the south camera defines world origin (Z=0).
                - the axis originating at south camera optical center and passing at world origin defines Y+.
            The world coordinates can be redefined by positioning user-defined frames in this native frame after
            calibration (see eg. 'add_target_frame' or 'add_pot_frame' methods)
        """
        if cameras is None:
            cameras = {}
        if targets is None:
            targets = {}
        if chessboards is None:
            chessboards = {}
        south_camera_id, south_inclination, south_distance = south_camera
        cameras = {camera_id: dict(inclination=inclination,
                                   distance=distance,
                                   rotation_to_south=rotation_to_south)
                   for camera_id, (inclination, distance, rotation_to_south) in cameras.items()
                   }
        cameras.update({south_camera_id: dict(inclination=south_inclination,
                                                    distance=south_distance,
                                                    rotation_to_south=0)})
        self.layout = dict(south_camera=south_camera_id,
                           cameras=cameras,
                           targets={target_id: dict(inclination=inclination,
                                                    rotation_to_south=rotation_to_south)
                                    for target_id, (inclination, rotation_to_south) in targets.items()
                                    },
                           chessboards={target_id: dict(between_corners=between_corners,
                                                        corners_h=corners_h,
                                                        corners_v=corners_v)
                                        for target_id, (between_corners, corners_h, corners_v) in chessboards.items()
                                        }
                           )
        self.image_paths = image_paths
        self.clockwise = clockwise_rotation
        self.world_unit = world_unit
        self.data_dir = data_dir
        self.calibration_dir = calibration_dir

        self.image_points = {target_id: defaultdict(dict) for target_id in targets}
        self.image_resolutions = defaultdict(dict)
        self.image_sizes = defaultdict(dict)

        self._facings = defaultdict(dict)
        for camera_id, camera in self.layout['cameras'].items():
            for target_id, target in self.layout['targets'].items():
                self._facings[target_id].update({camera_id: target['rotation_to_south'] - camera['rotation_to_south']})

    def abspath(self, path):
        if self.data_dir is None:
            return path
        else:
            return os.path.join(self.data_dir, path)

    def alpha(self, rotation):
        angle = numpy.radians(rotation)
        if self.clockwise:
            angle *= -1
        return angle

    def aiming_angle(self, camera_id, target_id, rotation):
        """The angle between camera Z- (opposite camera look-at axis) and target Z+ for a given rotation"""
        px, py, pz = 0, 0, 0
        rx, ry, rz = 0, 0, 0
        rx += numpy.radians(self.layout['targets'][target_id]['inclination'])
        rz += self.alpha(rotation - self.layout['targets'][target_id]['rotation_to_south'])
        fr_target = CalibrationFrame.frame(px, py, pz, rx, ry, rz)
        #
        px, py, pz = 0, 0, 0
        rx, ry, rz = numpy.pi, 0, 0
        rx += numpy.radians(self.layout['cameras'][camera_id]['inclination'])
        rz += self.alpha(self.layout['cameras'][camera_id]['rotation_to_south'])
        fr_camera = CalibrationFrame.frame(px, py, pz, rx, ry, rz)
        return angle3(fr_target.global_vec((0, 0, 1)), fr_camera.global_vec((0, 0, -1)))

    def quadrant_mask(self, quadrant, image):
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        mask = numpy.empty_like(image)
        h, w = mask.shape
        if quadrant == 'North':
            mask[:h//2, :] = 255
        elif quadrant == "South":
            mask[h // 2:, :] = 255
        elif quadrant == 'West':
            mask[:, :w//2] = 255
        elif quadrant == 'East':
            mask[:, w//2:] = 255
        else:
            raise ValueError('Unimplemented quadrant: ' + quadrant)
        return mask

    def roi_mask(self, roi, image):
        mask = numpy.zeros_like(image)
        contour = numpy.array(roi)
        cv2.fillPoly(mask, pts=[contour], color=(255, 255, 255))
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        return mask

    def target_masks(self, calibration, cameras=None, targets=None):
        """generate target mask from prior-calibration"""

        consider = {}
        if cameras is None:
            consider = {k: list(v) for k, v in self.image_paths.items()}
        elif isinstance(cameras, str):
            consider = {cameras: list(self.image_paths[cameras])}
        else:
            for item in cameras:
                if isinstance(item, str):
                    camera_id = item
                    rotation_list = list(self.image_paths[camera_id])
                else:
                    camera_id, rotation_list = item
                consider[camera_id] = rotation_list

        if targets is None:
            targets = list(self.layout['chessboards'])

        masks = {}
        for target_id in targets:
            masks[target_id] = []
            for camera_id, rotation_list in consider.items():
                for rotation in rotation_list:
                    masks[target_id].append((camera_id,
                                             rotation,
                                             calibration.target_mask(camera_id, target_id, rotation)
                                             )
                                            )
        return masks
    def detect_corners(self, cameras=None, masks=None, maximal_aiming_angle=65):
        """ Detection of pixel coordinates of chessboard corner points

        Args:
            cameras: a string or a list of elements specifying on which images should the detection be done. Element
                     can either be a camera_id string or a (camera_id, list_of_angles) tuple specifying which angle to
                     consider. If no angle are provided, all angles are considered. If cameras is None (default), all
                     images are used
            masks: a {target_id : [(camera_id, rotation, mask),...],...} dict of list of tuples specifying if a mask should
                    be applied to the image before detection. mask can either be a string specifying the image quadrant
                    ('North', 'South', 'East' or 'West') containing the target, a list of image coordinates (u,v) specifying
                    the Region of Interest containing the target.
            maximal_aiming_angle: images with a target that form an angle superior to this value are skipped
        """

        consider = {}
        if cameras is None:
            consider = {k: list(v) for k, v in self.image_paths.items()}
        elif isinstance(cameras, str):
            consider = {cameras: list(self.image_paths[cameras])}
        else:
            for item in cameras:
                if isinstance(item, str):
                    camera_id = item
                    rotation_list = list(self.image_paths[camera_id])
                else:
                    camera_id, rotation_list = item
                consider[camera_id] = rotation_list

        mask_dict = {}
        if masks is not None:
            mask_dict = {tid: defaultdict(dict) for tid in masks}
            for tid, list_items in masks.items():
                for cid, rot, mask in list_items:
                    mask_dict[tid][cid][rot] = mask

        for target_id, c in self.layout['chessboards'].items():
            chessboard = Chessboard(square_size=c['between_corners'],
                                    shape=(c['corners_h'], c['corners_v']),
                                    facing_angles=self._facings[target_id])
            for camera_id, rotation_list in consider.items():
                for rotation in rotation_list:
                    path = self.image_paths[camera_id][rotation]
                    found = False
                    aiming_angle = self.aiming_angle(camera_id, target_id, rotation)
                    if aiming_angle > maximal_aiming_angle:
                        print("Target {} Camera {} Angle {} - Skipped (angle {} > maximal_aiming_angle)".format(target_id, camera_id,
                                                                                        str(rotation),
                                                                                        str(aiming_angle)))
                    else:
                        image = cv2.imread(self.abspath(path), cv2.IMREAD_GRAYSCALE)
                        if target_id in mask_dict:
                            if camera_id in mask_dict[target_id]:
                                if rotation in mask_dict[target_id][camera_id]:
                                    mask = mask_dict[target_id][camera_id][rotation]
                                    if isinstance(mask, str):
                                        mask = self.quadrant_mask(mask, image)
                                    else:
                                        mask = self.roi_mask(mask, image)
                                    image = numpy.bitwise_and(image, mask)
                        found = chessboard.detect_corners(camera_id, rotation, image, check_order=True, image_id=path)
                        print("Target {} Camera {} Angle {} - Chessboard corners {}".format(target_id, camera_id,
                                                                                            str(rotation),
                                                                                            "found" if found else "not found"))
                    if found:
                        self.image_points[target_id][camera_id][rotation] = chessboard.image_points[camera_id][rotation]
            self.image_sizes.update(chessboard.image_sizes)
            for c, res in chessboard.image_resolutions().items():
                self.image_resolutions[c][target_id] = res

    def target_points(self):
        """extract target local3d point"""
        target_points = {}
        for target_id, d in self.layout['chessboards'].items():
            if target_id in self.image_points:
                chessboard = Chessboard(square_size=d['between_corners'],
                                        shape=(d['corners_h'], d['corners_v']),
                                        facing_angles=self._facings[target_id])
                chessboard.image_points = self.image_points[target_id]
                target_points[target_id] = chessboard.get_corners_local_3d()
        return target_points

    def calibrate(self, verbose=True):
        """Compute calibration"""
        cameras = {camera_id: (d['distance'], d['inclination'])
                   for camera_id, d in self.layout['cameras'].items()}
        targets = {target_id: (0, d['inclination'])
                   for target_id, d in self.layout['targets'].items()}
        resolutions = {k:numpy.mean(list(v.values())) for k, v in self.image_resolutions.items()}
        setup = CalibrationSetup(cameras, targets, resolutions, self.image_sizes, self._facings,
                                 self.clockwise)
        reference_target = next(iter(self._facings))
        reference_camera = self.layout['south_camera']
        cameras, targets, reference_camera, clockwise = setup.setup_calibration(reference_camera=reference_camera,
                                                                                reference_target=reference_target)
        target_points = {}
        image_points = defaultdict(dict)
        for target_id, d in self.layout['chessboards'].items():
            if target_id in self.image_points:
                chessboard = Chessboard(square_size=d['between_corners'],
                                        shape=(d['corners_h'], d['corners_v']),
                                        facing_angles=self._facings[target_id])
                chessboard.image_points = self.image_points[target_id]
                target_points[target_id] = chessboard.get_corners_local_3d()
                for camera_id in self.image_points[target_id]:
                    image_points[camera_id][target_id] = chessboard.get_corners_2d(camera_id)

        calibration = CalibrationSolver(targets=targets, cameras=cameras,
                                        target_points=target_points, image_points=image_points,
                                        reference_camera=reference_camera,
                                        clockwise_rotation=clockwise)
        # Three steps calibration yield better results than direct calibration
        calibration.calibrate(fit_cameras=False, verbose=verbose)
        if len(cameras) > 1:
            calibration.calibrate(fit_angle_factor=False, fit_reference_camera=False, fit_targets=False, verbose=verbose)
            calibration.calibrate(verbose=verbose)
        return calibration

    def target_frame(self, calibration):
        """Add a new world frame in calibration, similar to native frame, but whose origin is at the mean height of
        targets centers"""
        z_moy = numpy.mean([fr._pos_z for fr in calibration._targets.values()])
        return CalibrationFrame.from_tuple((0, 0, z_moy, 0, 0, 0))

    def pot_frame(self, v_pot, rail_orientation, calibration, dl=2000):
        """Add a new world frame to calibration based orientation (x-axis) chosen from top and
            origin chosen on side image"""
        p = calibration.get_projection('side', 0, 'native')
        pt = calibration.get_projection('top', 0, 'native')
        origin = (0, 0, 0)
        u, v = p(origin)
        du, dv = numpy.diff(p([origin, (0, 0, -dl)]), axis=0)[0]
        ut, vt = pt(origin)
        dut, dvt = numpy.diff(pt([origin, (0, 0, -dl)]), axis=0)[0]
        utp, vtp = ut + dut / dv * (v_pot - v), vt + dvt / dv * (v_pot - v)
        alpha_p = numpy.radians(rail_orientation)
        frame_points = [origin, (0, 'y', 0)]
        image_points = {'side': [(u + du / dv * (v_pot - v), v_pot), None],
                        'top': [None, (utp + numpy.cos(alpha_p) * dl, vtp - numpy.sin(alpha_p) * dl)]}
        pot_frame, _ = calibration.find_frame(image_points, frame_points,
                                              fixed_parameters={'_pos_x': 0, '_pos_y':0, '_rot_x':0, '_rot_y':0},
                                              start={'_pos_z': 0, '_rot_z': -numpy.pi / 2})
        return pot_frame
    def check_dir(self, path):
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def check_target_masks(self, masks, resize=0.25):
        outdir = os.path.join(self.calibration_dir, 'check_target_masks')
        for target_id, list_items in masks.items():
            for camera_id, rotation, mask in list_items:
                target_image = cv2.imread(self.abspath(self.image_paths[camera_id][rotation]))
                path = os.path.join(outdir, '_'.join([target_id, camera_id, str(rotation)]) + '.jpg')
                if isinstance(mask, str):
                    mask = self.quadrant_mask(mask, target_image)
                else:
                    mask = self.roi_mask(mask, target_image)
                masked = cv2.bitwise_and(target_image, target_image, mask=mask)
                shape = [int(i * resize) for i in target_image.shape[:2]]
                resized = cv2.resize(masked, shape, interpolation=cv2.INTER_AREA)
                self.check_dir(path)
                cv2.imwrite(path, resized)

    def check_image_points(self, resize=0.25):
        outdir = os.path.join(self.calibration_dir, 'check_image_points')
        for target_id in self.image_points:
            c = self.layout['chessboards'][target_id]
            chessboard_shape = (c['corners_h'], c['corners_v'])
            for camera_id in self.image_points[target_id]:
                for rotation, img_pts in self.image_points[target_id][camera_id].items():
                    image_path = self.image_paths[camera_id][rotation]
                    img = cv2.imread(self.abspath(self.image_paths[camera_id][rotation]))
                    img = cv2.drawChessboardCorners(img, chessboard_shape, img_pts, True)
                    shape = [int(i * resize) for i in img.shape[:2]]
                    resized = cv2.resize(img, shape, interpolation=cv2.INTER_AREA)
                    path = os.path.join(outdir, '_'.join([target_id, camera_id, str(rotation)]) + '.jpg')
                    self.check_dir(path)
                    cv2.imwrite(path, resized)

    def check_target_frame(self, calibration, resize=0.25, l=100):
        outdir = os.path.join(self.calibration_dir, 'check_target_frame')
        if 'target' not in calibration.frames:
            calibration.frames['target'] = self.target_frame(calibration)
        for camera_id, rot_dict in self.image_paths.items():
            for rotation, path in rot_dict.items():
                img = cv2.imread(self.abspath(path))
                frame_lines = calibration.frame_lines(camera_id, rotation, frame='target', l=l)
                for origin, end, col, w in frame_lines:
                    cv2.line(img, origin, end, col, w)
                shape = [int(i * resize) for i in img.shape[:2]]
                resized = cv2.resize(img, shape, interpolation=cv2.INTER_AREA)
                path = os.path.join(outdir, '_'.join([camera_id, str(rotation)]) + '.jpg')
                self.check_dir(path)
                cv2.imwrite(path, resized)


    def save_image_points(self, prefix=None):
        """save image points to calibration dir
        """
        for target_id, image_points in self.image_points.items():
            c = self.layout['chessboards'][target_id]
            chessboard = Chessboard(square_size=c['between_corners'],
                                    shape=(c['corners_h'], c['corners_v']),
                                    facing_angles=self._facings[target_id])
            chessboard.image_points = image_points
            chessboard.image_sizes = self.image_sizes
            #TODO filter non useed ids
            chessboard.image_ids = self.image_paths
            if prefix is None:
                items = []
            else:
                items = [prefix]
            items += ['image_points', target_id]
            path = os.path.join(self.calibration_dir, '_'.join(items) + '.json')
            self.check_dir(path)
            chessboard.dump(path)

    def load_image_points(self, image_points=None):
        """load image points
        """
        for target_id in self.layout['chessboards']:
            if image_points is not None and target_id in image_points:
                chessboard = image_points[target_id]
            else:
                items = ['image_points', target_id]
                path = os.path.join(self.calibration_dir, '_'.join(items) + '.json')
                chessboard = Chessboard.load(path)
            self.image_points[target_id] = chessboard.image_points
            self.image_paths = chessboard.image_ids
            self.image_sizes.update(chessboard.image_sizes)
            for c, res in chessboard.image_resolutions().items():
                self.image_resolutions[c][target_id] = res

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
        c._focal_length_x = f
        c._aspect_ratio = 1
        c._pos_x, c._pos_y, c._pos_z = px, py, pz
        c._rot_x, c._rot_y, c._rot_z = normalise_angle(rx),  normalise_angle(ry), normalise_angle(rz)

        return c


class CalibrationSolver(Calibration):
    """A class for calibration of multi-views imaging systems (fixed cameras, rotating targets)"""

    def __init__(self, angle_factor=1, targets=None, cameras=None, target_points=None, image_points=None,
                 reference_camera='side', clockwise_rotation=True, calibration_statistics=None, frames=None):
        """Instantiate a Calibration object with calibration data

        Args:
            angle_factor: start value for angle_factor. angle_factor is a float multiplier of rotation consign
                to obtain actual rotation angle (default value: 1)
            targets: a {target_id : CalibrationFrame,...} dict of targets to be used as starting guess for target frames,
                positioned using transformations of the base configuration of the imaging system (see CalibrationLayout)
            cameras: a {camera_id: CalibrationCamera,...} dict of cameras to be used as starting guess for cameras,
                positioned using transformations of the base configuration of the imaging system (see CalibrationLayout)
            target_points: a {target_id: [(x, y, z), ...], ...} dict of coordinates of target corner points, expressed
                in target local frame or native world frame if target_id == 'world'
            image_points: a {camera_id: {target_id : {rotation : [(u,v),...], ...}, ...,} dict of dict of dict of
                pixel coordinates of target corner points  projected on camera images at a given rotation consign. The
                rotation consign is the rounded angle (degrees) by which the turntable has turned before image acquisition
            reference_camera (str): camera_id of the camera to be used to define world native frame (see details)
            clockwise_rotation (bool): are targets rotating clockwise ? (default True)
            calibration_statistics (dict): statitistics of current calibration
            frames (dict): a {frame_name: CalibrationFrame, ...} dict of user-defined frames positioned in world
            native frame specifying alternative coordinates systems

        Details:
            Calibration allows finding position and parameters of cameras and targets and compute the projection
            functions of cameras from different use-defined frames
            The world 3D coordinates are natively expressed in the frame defined by the axis of rotation and a reference
            camera as follow:
                - The axis of rotation of the rotating system, oriented toward the sky, defines the world  Z+.
                - The altitude of the reference camera defines Z=0.
                - The vertical plane around Z+ intercepting the reference camera, oriented from the camera to the axe of
                rotation, defines world Y+ axis
            The world coordinates can be redefined by further positioning user-defined frames in this native frame.
        """

        super().__init__(angle_factor=angle_factor, targets=targets, cameras=cameras, target_points=target_points, reference_camera=reference_camera,
                         clockwise_rotation=clockwise_rotation, calibration_statistics=calibration_statistics,
                         frames=frames)
        self._image_points = {}
        self._nb_image_points = 0

        self.set_values(image_points= image_points)

        self.fit_angle_factor = True
        self.fit_aspect_ratio = True
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

        self._nb_image_points = 0
        for cam_pts in self._image_points.values():
            for im_pts_t in cam_pts.values():
                for im_pts in im_pts_t.values():
                    self._nb_image_points += len(im_pts)

    @staticmethod
    def from_dict(save_class):
        c = CalibrationSolver()
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

    def split_parameters(self, x0):
        # decompose x0 into angle_factor, reference camera, targets and cameras list of parameters
        # number of parameters per above mentioned items
        nbp_target = 6
        nbp_camera = 8 if self.fit_aspect_ratio else 7
        nb_pars = [0, 0, 0, 0]
        if self.fit_angle_factor:
            nb_pars[0] = 1
        if self.fit_reference_camera:
            nb_pars[1] = 6 if self.fit_aspect_ratio else 5
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

    def fit_errors(self, x0):

        turntable, ref_cam, targets, cameras = self.split_parameters(x0)

        # merge ref_cam to cameras
        if len(ref_cam) > 0:
            _pos_x = 0
            _pos_z = 0
            if self.fit_aspect_ratio:
                _focal_length_x, _aspect_ratio, \
                _pos_y, \
                _rot_x, _rot_y, _rot_z = ref_cam
                ref_cam = [_focal_length_x, _aspect_ratio,
                           _pos_x, _pos_y, _pos_z,
                           _rot_x, _rot_y, _rot_z]
            else:
                _focal_length_x, \
                _pos_y, \
                _rot_x, _rot_y, _rot_z = ref_cam
                ref_cam = [_focal_length_x,
                           _pos_x, _pos_y, _pos_z,
                           _rot_x, _rot_y, _rot_z]
            cameras.insert(0, ref_cam)

        # build frames
        angle_factor = self.angle_factor
        if len(turntable) > 0:
            angle_factor = turntable[0]

        target_frames = []
        if 'world' in self._targets_points:
            target_frames += [self.get_frame('native')]
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
            if self.fit_aspect_ratio:
                _focal_length_x, _aspect_ratio, \
                _pos_x, _pos_y, _pos_z, \
                _rot_x, _rot_y, _rot_z = camera
            else:
                _aspect_ratio = 1
                _focal_length_x, \
                _pos_x, _pos_y, _pos_z, \
                _rot_x, _rot_y, _rot_z = camera
            camera_frames.append(CalibrationCamera.frame(_pos_x, _pos_y, _pos_z,
                                                         _rot_x, _rot_y, _rot_z))
            camera_focals.append([_focal_length_x, _aspect_ratio])

        err = {}
        # cameras and image_points in the right order
        cams = []
        im_pts_cam = []
        labels = []
        if len(ref_cam) > 0:
            cams += [self._cameras[self.reference_camera]]
            im_pts_cam += [self._image_points[self.reference_camera]]
            labels += [self.reference_camera]
        cams += [self._cameras[k] for k in self._cameras if k != self.reference_camera]
        im_pts_cam += [self._image_points[k] for k in self._cameras if k != self.reference_camera]
        labels += [k for k in self._cameras if k != self.reference_camera]
        # target_points in the right order
        target_points = self._targets_points.get('world', [])
        if len(target_points) > 0:
            target_points = [target_points] # target_points is a list of list of points
        target_points += [self._targets_points[k] for k in self._targets]

        for fr_cam, focals, camera, im_pts_c, lab in zip(camera_frames, camera_focals, cams, im_pts_cam, labels):
            _targets = ['world'] if 'world' in self._targets_points else []
            _targets += [k for k in self._targets]
            im_pts_t = [im_pts_c[k] for k in _targets]
            for fr_target, t_pts, im_pts,t_name in zip(target_frames, target_points, im_pts_t, _targets):
                for rotation, ref_pts in im_pts.items():
                    fr_table = CalibrationSolver.turntable_frame(rotation, angle_factor, self.clockwise)
                    target_pts = fr_table.global_point(fr_target.global_point(t_pts))
                    _focal_length_x, _aspect_ratio = focals
                    pts = CalibrationCamera.pixel_coordinates(fr_cam.local_point(target_pts),
                                                              camera._width_image,
                                                              camera._height_image,
                                                              _focal_length_x,
                                                              _aspect_ratio)
                    err['_'.join([lab, t_name, str(rotation)])]=numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self.verbose:
            print(sum(err.values()))

        return err

    def fit_function(self, x0):
        err = self.fit_errors(x0)
        return sum(err.values())

    def get_parameters(self):
        parameters = []
        if self.fit_angle_factor:
            parameters.append(self.angle_factor)
        if self.fit_reference_camera:
            c = self._cameras[self.reference_camera]
            parameters += [c._focal_length_x]
            if self.fit_aspect_ratio:
                parameters += [c._aspect_ratio]
            parameters += [c._pos_y, c._rot_x, c._rot_y, c._rot_z]
        if self.fit_targets:
            for id_target,t in self._targets.items():
                parameters += [t._pos_x, t._pos_y, t._pos_z,
                               t._rot_x, t._rot_y, t._rot_z]
        if self.fit_cameras:
            for id_camera, c in self._cameras.items():
                if id_camera != self.reference_camera:
                    parameters += [c._focal_length_x]
                    if self.fit_aspect_ratio:
                        parameters += [c._aspect_ratio]
                    parameters += [c._pos_x, c._pos_y, c._pos_z,
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
                before['fit_aspect_ratio'] = self.fit_aspect_ratio
                before['fit_reference_camera'] = self.fit_reference_camera
                before['fit_targets'] = self.fit_targets
                before['fit_cameras'] = self.fit_cameras
                self.fit_angle_factor = True
                self.fit_aspect_ratio = True
                self.fit_reference_camera = True
                self.fit_targets = True
                self.fit_cameras = True

            p = self.get_parameters()
            err = self.fit_function(p)

            if all_pars:
                self.fit_angle_factor = before['fit_angle_factor']
                self.fit_aspect_ratio = before['fit_aspect_ratio']
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
            d_origin = camera.distance_to_origin
            pixel_size = camera.pixel_size_at_origin
            calibration_images = {}
            if self._nb_image_points > 0:
                for target in self._image_points[id_camera]:
                    calibration_images[target] = len(self._image_points[id_camera][target])
            stats[id_camera] = {'distance to origin': d_origin,
                                'pixel_size': pixel_size,
                                'target_images': calibration_images}
        return stats


    def calibrate(self, fit_angle_factor=True, fit_aspect_ratio=True, fit_reference_camera=True, fit_targets=True, fit_cameras=True,
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
        self.fit_aspect_ratio = fit_aspect_ratio
        self.fit_reference_camera = fit_reference_camera
        self.fit_targets = fit_targets
        self.fit_cameras = fit_cameras
        self.verbose = verbose

        parameters = self.find_parameters()

        turntable, ref_cam, target_pars, camera_pars = self.split_parameters(parameters)

        pos_labels = ['_pos_x', '_pos_y', '_pos_z']
        rot_labels = ['_rot_x', '_rot_y', '_rot_z']
        f_labels = ['_focal_length_x']
        if self.fit_aspect_ratio:
            f_labels += ['_aspect_ratio']

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
            cams = [self._cameras[k] for k in self._cameras if k != self.reference_camera]
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
        """ Find native 3D world coordinates of points from paired image coordinates on multiple cameras

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
            start = numpy.array([(0, 0, 0)] * len(list(image_points.values())[0]))

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

    def find_camera(self, image_points, target_points, image_size=None, fixed_parameters=None, guess=None,  niter=10):
        """ Find camera parameters from clicked image points of known 3D target points

        Args:
            image_points: an array-like list of image coordinates of remarkable points
            target_points: an array-like list of 3D coordinates of remarkable points
            image_size: (width, height) tuple describing image dimension (pixels). Alternatively the name of an existing
                camera with the same shape. If None, the shape of the reference camera is used
            fixed_parameters: a {parameter_name: value} dict of fixed (unfitted) camera parameters. Valid parameters
             names are '_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z', '_focal_length_x', '_aspect_ratio'
            guess : a guessed Calibration camera
            niter: (int) the number of iteration of the basin-hopping optimisation algorithm

        Returns:
            A calibrated CalibrationCamera
        """

        image_points = numpy.array(image_points)
        target_points = numpy.array(target_points)

        if fixed_parameters is None:
            fixed_parameters = {}

        if isinstance(image_size, tuple):
            w, h = image_size
        elif isinstance(image_size, str):
            if image_size in self._cameras:
                h, w = self.get_image_shape(image_size)
        else:
            h, w = self.get_image_shape(self.reference_camera)
        fixed_parameters.update({'_width_image': w, '_height_image': h})

        pars = ('_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z', '_width_image', '_height_image',
                '_focal_length_x', '_aspect_ratio')
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

    def find_frame(self, image_points, frame_points, fixed_parameters=None, start=None):
        """ Find Frame parameters and 3D local (frame based) coordinates of points from paired image coordinates

        Args:
            image_points: a {camera_id: [(u1,v1),...], ...} dict of list of pixel coordinates of frame points
            frame_points: an array-like list of 3D points coordinates, expressed in local coordinate of the searched frame.
                keywords 'x', 'y' and 'z' can be used to specify an unknown coordinate
            fixed_parameters: a {parameter_name: value} dict of fixed (unfitted) frame parameters. Valid parameters
             names are '_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z'
             start : a frame to be used as guess

        Returns:
            A CalibrationFrame and the list of 3D coordinates matching frame_points

        """

        if fixed_parameters is None:
            fixed_parameters = {}

        image_points = {k: numpy.array(v) if v is not None else v for k, v in image_points.items()}

        # free frame parameters
        pars = ('_pos_x', '_pos_y', '_pos_z', '_rot_x', '_rot_y', '_rot_z')
        free_pars = [p for p in pars if p not in fixed_parameters]
        n_free_pars = len(free_pars)


        # unknown coordinates
        n_free_x, n_free_y, n_free_z = 0, 0, 0
        for pt in frame_points:
            if 'x' in pt:
                n_free_x += 1
            if 'y' in pt:
                n_free_y += 1
            if 'z' in pt:
                n_free_z += 1

        if start is None:
            start = numpy.zeros(n_free_pars + n_free_x + n_free_y + n_free_z)
        else:
            start = [start[p] for p in free_pars] + numpy.zeros(n_free_x + n_free_y + n_free_z).tolist()

        def split_parameters(x0):
            nb_pars = [n_free_pars, n_free_x, n_free_y, n_free_z]
            xx0 = iter(x0)
            frame_pars, free_x, free_y, free_z = [list(islice(xx0, n)) for n in nb_pars]
            frame_pars = dict(zip(free_pars, frame_pars))
            frame_pars.update(fixed_parameters)
            fr_points = []
            for x, y, z in frame_points:
                if x == 'x':
                    x = free_x.pop()
                if y == 'y':
                    y = free_y.pop()
                if z == 'z':
                    z = free_z.pop()
                fr_points.append((x,y,z))
            return frame_pars, fr_points

        def fit_function(x0):
            frame_pars, fr_points = split_parameters(x0)
            cframe = CalibrationFrame()
            cframe.set_vars(frame_pars)
            fr = cframe.get_frame()
            pts = fr.global_point(fr_points)

            err = 0
            for id_camera in image_points:
                im_pts = [p for p in image_points[id_camera] if p is not None]
                world_pts = [p for p, im_p in zip(pts, image_points[id_camera]) if im_p is not None]
                proj = self.get_projection(id_camera, 0)
                pix = proj(world_pts)
                err += numpy.linalg.norm(pix - im_pts, axis=1).sum()
            print(err)

            return err


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

