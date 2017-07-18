# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import cv2
import glob
import os
import collections
import pkg_resources

from alinea.phenomenal.calibration import (
    Chessboard)

from alinea.phenomenal.calibration import (
    CalibrationCameraSideWith2Target,
    CalibrationCameraTop)

from alinea.phenomenal.data_structure import (
    VoxelPointCloud)

# ==============================================================================

__all__ = ["plant_1_images",
           "plant_1_images_binarize",
           "plant_1_chessboards",
           "plant_1_calibration_camera_side",
           "plant_1_calibration_camera_top",
           "plant_1_voxel_point_cloud",
           "plant_2_voxel_point_cloud"]

# ==============================================================================


def plant_1_images():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/images/')

    # data = pkgutil.get_data('alinea.phenomenal',
    #                         'share/data/plant_1/images/*.png')

    files_path = glob.glob(data_directory + '*.png')

    images = collections.defaultdict(lambda: collections.defaultdict())

    for path in files_path:
        basename = os.path.basename(path)
        id_camera = basename.split('_')[0]
        angle = int(((basename.split('_')[1]).split('.png'))[0])

        images[id_camera][angle] = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    return images


def plant_1_images_chessboard():
    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/images_chessboard/')

    files_path = glob.glob(data_directory + '*.png')
    files_name = [os.path.basename(path) for path in files_path]

    angles = map(lambda x: int((x.split('.png')[0])), files_name)

    images_chessboard = dict()
    for i in range(len(files_path)):
        images_chessboard[angles[i]] = cv2.imread(
            files_path[i], cv2.IMREAD_UNCHANGED)

    return images_chessboard


def plant_1_images_binarize():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/images_binarize/')

    files_path = glob.glob(data_directory + '*.png')
    files_name = [os.path.basename(path) for path in files_path]

    angles = map(lambda x: int((x.split('.png')[0])), files_name)

    images = dict()
    for i in range(len(files_path)):
        images[angles[i]] = cv2.imread(files_path[i], cv2.IMREAD_GRAYSCALE)

    return images


def plant_1_mask_meanshift():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_mean_shift.png')

    mask_mean_shift = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_mean_shift


def plant_1_mask_hsv():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_hsv.png')

    mask_hsv = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_hsv


def plant_1_mask_clean_noise():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_clean_noise.png')

    mask_clean_noise = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_clean_noise


def plant_1_mask_adaptive_threshold():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_adaptive_threshold.png')

    mask_adaptive_threshold = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_adaptive_threshold


def plant_1_mask_elcom_mean_shift():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_elcom_mean_shift.png')

    mask_elcom_mean_shift = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_elcom_mean_shift


def plant_1_mask_elcom_hsv():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_elcom_hsv.png')

    mask_elcom_hsv = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)

    return mask_elcom_hsv


def plant_1_mask_hsv_roi_main():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_hsv_roi_main.png')

    mask_hsv_roi_main = cv2.imread(file_path, flags=cv2.IMREAD_GRAYSCALE)

    return mask_hsv_roi_main


def plant_1_mask_hsv_roi_band():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_hsv_roi_band.png')

    mask_hsv_roi_band = cv2.imread(file_path, flags=cv2.IMREAD_GRAYSCALE)

    return mask_hsv_roi_band


def plant_1_mask_hsv_roi_pot():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/mask_hsv_roi_pot.png')

    mask_hsv_roi_pot = cv2.imread(file_path, flags=cv2.IMREAD_GRAYSCALE)

    return mask_hsv_roi_pot


def plant_1_background_hsv():

    file_path = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data/plant_1/mask/background_hsv.png')

    background_hsv = cv2.imread(file_path, flags=cv2.IMREAD_COLOR)

    return background_hsv


def plant_1_chessboards():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    chess_1 = Chessboard.load(
        data_directory + 'chessboard_2013-07-11_15-49-42_vis_wide_chess_1')

    chess_2 = Chessboard.load(
        data_directory + 'chessboard_2013-07-11_15-49-42_vis_wide_chess_2')

    return chess_1, chess_2


def plant_1_calibration_camera_side():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    file_path = data_directory + 'calibration_camera_side'

    return CalibrationCameraSideWith2Target.load(file_path)


def plant_1_calibration_camera_top():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    file_path = data_directory + 'calibration_camera_top'

    return CalibrationCameraTop.load(file_path)


def plant_1_params_camera_opencv_path():
    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    params_camera_opencv_path = data_directory + 'params_camera_opencv'

    return params_camera_opencv_path


def plant_1_voxel_point_cloud(voxels_size=10):
    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    if 3 <= int(voxels_size) <= 20:

        filename = ("{data_directory}"
                    "voxel_centers_size_"
                    "{voxels_size}.xyz".format(
                                        data_directory=data_directory,
                                        voxels_size=str(int(voxels_size))))

        return VoxelPointCloud.read_from_xyz(filename, voxels_size)

    return None


def plant_2_voxel_point_cloud(voxels_size=10):

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_2/')

    if 3 <= int(voxels_size) <= 20:

        filename = ("{data_directory}"
                    "ZA16__0001_Lo1270_H_ZM2887_"
                    "d151_WD_3_01_01_ARCH2016-04-15_"
                    "_2016-05-20_06-52-56.492283.npz".format(
                                        data_directory=data_directory,
                                        voxels_size=str(int(voxels_size))))

        return VoxelPointCloud.read_from_npz(filename)

    return None


def plant_1_voxels_size_4_without_loss_120():

    data_directory = pkg_resources.resource_filename(
        'alinea.phenomenal', 'data//plant_1/')

    filename = data_directory + "voxel_centers_size_4_without_loss.json"

    return VoxelPointCloud.read_from_json(filename)
