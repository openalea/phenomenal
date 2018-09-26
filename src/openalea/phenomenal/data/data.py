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

from ..mesh import read_ply_to_vertices_faces
from ..calibration import (Chessboard, CalibrationCamera)
from ..object import VoxelGrid
# ==============================================================================


def _path_images(plant_number=1, dtype="bin"):
    """ According to the plant number return a dict[id_camera][angle] containing
    filename of file.

    Parameters
    ----------
    plant_number : int

    dtype :  "bin" or "raw" or "chessboard"

    Returns
    -------
    d : dict of dict of string
        dict[id_camera][angle] = filename
    """
    data_directory = pkg_resources.resource_filename(
        'openalea.phenomenal', 'data/plant_{}/{}/'.format(
            plant_number, dtype))

    d = collections.defaultdict(dict)
    for id_camera in ["side", "top"]:
        filenames = glob.glob(os.path.join(data_directory, id_camera, '*.png'))
        for filename in filenames:
            angle = int(os.path.basename(filename).split('.png')[0])
            d[id_camera][angle] = filename

    return d


def path_bin_images(plant_number=1):
    """ According to the plant number return a dict[id_camera][angle] containing
    filename of the binary image.

    Parameters
    ----------
    plant_number : int
        Number of the plant desired
    Returns
    -------
    d : dict of dict of string
        dict[id_camera][angle] = filename
    """
    return _path_images(plant_number=plant_number, dtype="bin")


def path_raw_images(plant_number=1):
    """
    According to the plant number return a dict[id_camera][angle] containing
    filename of the raw image.
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera][angle] of filename
    """
    return _path_images(plant_number=plant_number, dtype="raw")


def path_chessboard_images(plant_number=1):
    """
    According to the plant number return a dict[id_camera][angle] containing
    filename of the raw image.
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera][angle] of filename
    """
    return _path_images(plant_number=plant_number, dtype="chessboard")


def raw_images(plant_number=1):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader raw image.
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera][angle] of loaded RGB image
    """

    d = path_raw_images(plant_number)
    for id_camera in d:
        for angle in d[id_camera]:
             img = cv2.imread(d[id_camera][angle], cv2.IMREAD_COLOR)
             d[id_camera][angle] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return d


def bin_images(plant_number=1):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader binary image.
    A binary image is a numpy array of uint8 type.
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera][angle] of loaded grayscale image
    """

    d = path_bin_images(plant_number)
    for id_camera in d:
        for angle in d[id_camera]:
            d[id_camera][angle] = cv2.imread(d[id_camera][angle],
                                             cv2.IMREAD_GRAYSCALE)
    return d


def chessboard_images(plant_number=1):
    """
    According to the plant number return a dict[id_camera][angle] of
    numpy array of the loader binary image.
    A binary image is a numpy array of uint8 type.
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera][angle] of loaded grayscale image
    """

    d = path_chessboard_images(plant_number)
    for id_camera in d:
        for angle in d[id_camera]:
            img = cv2.imread(d[id_camera][angle], cv2.IMREAD_COLOR)
            d[id_camera][angle] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return d,

# ==============================================================================


def chessboards(plant_number=1):
    """
    According to the plant number return a dict[id_camera] of camera
    calibration object
    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera] of camera calibration object
    """
    data_directory = pkg_resources.resource_filename(
        'openalea.phenomenal', 'data/plant_{}/chessboard/points/'.format(
            plant_number))

    chessboards = list()
    for id_chessboard in [1, 2]:
        chessboards.append(Chessboard.load(
            os.path.join(data_directory,
                         "chessboard_{}.json".format(id_chessboard))))

    return chessboards


def calibrations(plant_number=1):
    """
    According to the plant number return a dict[id_camera] of camera
    calibration object

    :param plant_number: number of the plant desired (int)
    :return: dict[id_camera] of camera calibration object
    """
    data_directory = pkg_resources.resource_filename(
        'openalea.phenomenal', 'data/plant_{}/calibration/'.format(
            plant_number))

    calibration = dict()
    for id_camera in ["side", "top"]:
        calibration[id_camera] = CalibrationCamera.load(
            os.path.join(data_directory,
                         "calibration_camera_{}.json".format(id_camera)))

    return calibration


def voxel_grid(plant_number=1, voxels_size=4):
    """
    According to the plant number and the voxel size desired return the
    voxel_grid of the plant.

    :param plant_number: number of the plant desired (int)
    :param voxels_size: diameter of each voxel in mm (int)
    :return: voxel_grid object
    """

    filename = pkg_resources.resource_filename(
        'openalea.phenomenal', 'data/plant_{}/voxels/{}.npz'.format(
            plant_number, voxels_size))

    vg = VoxelGrid.read(filename)

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


def synthetic_plant(plant_number=1, registration_point=(0, 0, 750)):
    """ According to the plant number return the mesh plant and skeleton of the
     synthetic plant.

    Parameters
    ----------
    plant_number : int, optional
        Number of the plant desired

    registration_point: 3-tuple, optional
        Position of the pot in the scene
    Returns
    -------
        out : vertices, faces, meta_data

    """
    filename = pkg_resources.resource_filename(
        'openalea.phenomenal',
        'data/synthetic_plant_{}/synthetic_plant.ply'.format(plant_number))

    vertices, faces, color = read_ply_to_vertices_faces(filename)
    vertices = numpy.array(vertices) * 10 - numpy.array([registration_point])

    with open(filename.replace("ply", "json"), 'r') as infile:
        meta_data = json.load(infile)

    return vertices, faces, meta_data

# ==============================================================================


def mesh_mccormik_plant(plant_number=1):
    filename = pkg_resources.resource_filename(
        'openalea.phenomenal',
        'data/mccormick_plant_{}/segmentedMesh.ply'.format(plant_number))

    vertices, faces, colors = read_ply_to_vertices_faces(filename)

    return vertices, faces, colors