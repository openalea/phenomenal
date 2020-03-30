# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import json
import numpy
import cv2
import glob
import os
import collections
import pkg_resources
import pathlib


from openalea.phenomenal.mesh import read_ply_to_vertices_faces
from openalea.phenomenal.calibration import (Chessboard, Calibration, OldCalibrationCamera)
from openalea.phenomenal.object import VoxelGrid
# ==============================================================================


def _path_images(name_dir, dtype="bin"):
    """ According to the plant number return a dict[id_camera][angle] containing
    filename of file.

    Parameters
    ----------

    dtype :  "bin" or "raw" or "chessboard"

    Returns
    -------
    d : dict of dict of string
        dict[id_camera][angle] = filename
    """
    data_directory = os.path.join(name_dir, '{}/'.format(dtype))

    d = collections.defaultdict(dict)
    for id_camera in ["side", "top"]:
        filenames = glob.glob(os.path.join(data_directory, id_camera, '*'))
        for filename in filenames:
            angle = int(pathlib.Path(filename).stem)
            d[id_camera][angle] = filename

    return d


def path_bin_images(name_dir):
    """ According to the plant number return a dict[id_camera][angle] containing
    filename of the binary image.

    Returns
    -------
    d : dict of dict of string
        dict[id_camera][angle] = filename
    """
    return _path_images(name_dir, dtype="bin")


def path_raw_images(name_dir):
    """
    According to the plant number return a dict[id_camera][angle] containing
    filename of the raw image.

    :return: dict[id_camera][angle] of filename
    """
    return _path_images(name_dir, dtype="raw")


def path_chessboard_images(name_dir):
    """
    According to the plant number return a dict[id_camera][angle] containing
    filename of the raw image.

    :return: dict[id_camera][angle] of filename
    """
    return _path_images(name_dir, dtype="chessboard")


def raw_images(name_dir):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader raw image.

    :return: dict[id_camera][angle] of loaded RGB image
    """

    d = path_raw_images(name_dir)
    for id_camera in d:
        for angle in d[id_camera]:
             img = cv2.imread(d[id_camera][angle], cv2.IMREAD_COLOR)
             d[id_camera][angle] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return d


def bin_images(name_dir):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader binary image.
    A binary image is a numpy array of uint8 type.

    :return: dict[id_camera][angle] of loaded grayscale image
    """

    d = path_bin_images(name_dir)
    for id_camera in d:
        for angle in d[id_camera]:
            d[id_camera][angle] = cv2.imread(d[id_camera][angle],
                                             cv2.IMREAD_GRAYSCALE)
    return d


def chessboard_images(name_dir):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader binary image.
    A binary image is a numpy array of uint8 type.

    :return: dict[id_camera][angle] of loaded grayscale image
    """

    d = path_chessboard_images(name_dir)
    for id_camera in d:
        for angle in d[id_camera]:
            img = cv2.imread(d[id_camera][angle], cv2.IMREAD_COLOR)
            d[id_camera][angle] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return d,

# ==============================================================================


def chessboards(name_dir):
    """
    According to name_dir return a dict[id_camera] of camera
    calibration object

    :return: dict[id_camera] of camera calibration object
    """
    data_directory = os.path.join(name_dir, 'chessboard/points/')

    chessboards = list()
    for id_chessboard in [1, 2]:
        chessboards.append(Chessboard.load(
            os.path.join(data_directory,
                         "chessboard_{}.json".format(id_chessboard))))

    return chessboards


def do_calibration(name_dir):
    """Regenerate calibration of cameras"""
    data_directory = os.path.join(name_dir, 'calibration')

    cbs = dict(zip(('target_1', 'target_2'), chessboards(name_dir)))
    # add missing info
    cb = cbs['target_1']
    cb.facing_angles = {'side': 48, 'top': 48}
    cb.image_sizes = {'side': (2056, 2454), 'top': (2454, 2056)}
    cb.check_order()
    #
    cb = cbs['target_2']
    cb.facing_angles = {'side': 228, 'top': 228}
    cb.image_sizes = {'side': (2056, 2454), 'top': (2454, 2056)}
    cb.check_order()

    chess_targets = Chessboards(cbs)
    image_sizes = chess_targets.image_sizes()
    image_resolutions = chess_targets.image_resolutions()
    facings = chess_targets.facings()
    target_points = chess_targets.target_points()
    image_points = chess_targets.image_points()

    cams = {'side': (5500, 90), 'top': (2500, 0)}
    targs = {'target_1': (100, 45), 'target_2': (100, 45)}
    start = CalibrationSetup(cams, targs, image_resolutions, image_sizes, facings,
                             clockwise_rotation=True)
    cameras, targets = start.setup_calibration(reference_camera='side', reference_target='target_1')
    calibration = Calibration(targets=targets, cameras=cameras,
                              target_points=target_points, image_points=image_points,
                              reference_camera='side', clockwise_rotation=True)
    calibration.calibrate()
    calibration.dump(os.path.join(data_directory, 'calibration_cameras.json'))



def calibrations(name_dir):
    """
    According to name_dir return a camera
    calibration object

    """

    calibration = dict()
    for id_camera in ["side", "top"]:
        calibration[id_camera] = OldCalibrationCamera.load(
            os.path.join(data_directory,
                         "calibration_camera_{}.json".format(id_camera)))


def new_calibrations(name_dir):
    """
    According to name_dir return a camera
    calibration object

    """

    file_name = os.path.join(name_dir, 'calibration', 'calibration_cameras.json')
    return Calibration.load(file_name)



def voxel_grid(plant_number=1, voxels_size=4):
    """
    According to the plant number and the voxel size desired return the
    voxel_grid of the plant.

    :param plant_number: number of the plant desired (int)
    :param voxels_size: diameter of each voxel in mm (int)
    :return: voxel_grid object
    """
    vg = VoxelGrid.read(
        os.path.join(name_dir,
                     'plant_{}/voxels/{}.npz'.format(plant_number,
                                                     voxels_size)))

    return vg

# ==============================================================================


def tutorial_data_binarization_mask():
    """
    Return the list of required images to process the notebook tutorial on
    binarization. The images are already load with opencv in unchanged format.
    images = ["mask_hsv.png", "mask_clean_noise.png", "mask_mean_shift.png"]

    :return: list of image
    """

    data_directory = pkg_resources.resource_filename(
        'openalea.phenomenal', 'data/plant_6/mask/')

    masks = list()
    for filename in ["mask_hsv.png",
                     "mask_mean_shift.png"]:

        masks.append(cv2.imread(os.path.join(data_directory, filename),
                                flags=cv2.IMREAD_GRAYSCALE))

    return masks

# ==============================================================================


def synthetic_plant(name_dir, registration_point=(0, 0, 750)):
    """ According to name_dir return the mesh plant and skeleton of the
     synthetic plant.

    Parameters
    ----------
    name_dir : str
        Name of the synthetic plant directory

    registration_point: 3-tuple, optional
        Position of the pot in the scene
    Returns
    -------
        out : vertices, faces, meta_data

    """
    filename = os.path.join(name_dir, 'synthetic_plant.ply')

    vertices, faces, color = read_ply_to_vertices_faces(filename)
    vertices = numpy.array(vertices) * 10 - numpy.array([registration_point])

    with open(filename.replace("ply", "json"), 'r') as infile:
        meta_data = json.load(infile)

    return vertices, faces, meta_data

# ==============================================================================


def mesh_mccormik_plant(name_dir):
    """ According to name_dir return the mesh of plant from the McCormik paper
    """

    filename = os.path.join(name_dir, 'segmentedMesh.ply')

    vertices, faces, colors = read_ply_to_vertices_faces(filename)

    return vertices, faces, colors