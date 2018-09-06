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

import cv2
import collections
import numpy

import openalea.phenomenal.calibration as phm_calib
import openalea.phenomenal.image as phm_img
import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.display as phm_display
# ==============================================================================
# ROUTINE CALIBRATION
# ==============================================================================


def detect_chessboard(chessboard_images,
                      size_of_chessboard=47,
                      shape_of_chessboard=(8, 6)):

    # BUILD CHESSBOARD OBJECT
    chessboard = phm_calib.Chessboard(size_of_chessboard,
                                      shape_of_chessboard)

    for id_camera in chessboard_images:
        for angle in chessboard_images[id_camera]:
            im = chessboard_images[id_camera][angle]
            found = chessboard.detect_corners(id_camera, angle, im)

    return [chessboard],


def calibrations(chessboards,
                 size_image=(2056, 2454),
                 number_of_repetition=1):

    id_cameras = ["side", "top"]
    calibrations = dict()
    for id_camera in id_cameras:
        calibration = None
        if len(chessboards) == 1:
            calibration = phm_calib.CalibrationCameraSideWith1Target()
            err = calibration.calibrate(chessboards[0].get_corners_2d(id_camera),
                                        chessboards[0].get_corners_local_3d(),
                                        size_image,
                                        number_of_repetition=number_of_repetition,
                                        # repetion here is 0 to optimize time consuming (for better result put 4)
                                        verbose=False)

        if len(chessboards) == 2:
            calibration = phm_calib.CalibrationCameraSideWith2TargetYXZ()
            err = calibration.calibrate(chessboards[0].get_corners_2d(id_camera),
                                        chessboards[0].get_corners_local_3d(),
                                        chessboards[1].get_corners_2d(id_camera),
                                        chessboards[1].get_corners_local_3d(),
                                        size_image,
                                        number_of_repetition=number_of_repetition,
                                        # repetion here is 0 to optimize time consuming (for better result put 4)
                                        verbose=False)

        calibrations[id_camera] = calibration

    # Error of reprojection (in pixel distance) for all point in the target (48)
    # So real error is err / 48

    return phm_data.calibrations(6)
    # return calibrations

# ==============================================================================
# ROUTINE BINARIZATION
# ==============================================================================


def routine_side_binarization(image, mean_img):
    maks = phm_data.tutorial_data_binarization_mask()

    threshold = 0.3
    dark_background = False

    hsv_min = (30, 11, 0)
    hsv_max = (129, 254, 141)

    # Convert image on HSV representation
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Threshold the image with HSV min and max value
    binary_hsv_image = phm_img.threshold_hsv(hsv_image, hsv_min, hsv_max,
                                             maks[0])

    # Threshold the image with difference between image and mean_image
    binary_mean_shift_image = phm_img.threshold_meanshift(
        image, mean_img, threshold, dark_background, maks[1])

    # Add the two image
    result = cv2.add(binary_hsv_image, binary_mean_shift_image)

    # Erode and dilate the image to remove possible noise
    result = cv2.medianBlur(result, 3)

    return result


def routine_top_binarization(image):
    hsv_min = (42, 75, 28)
    hsv_max = (80, 250, 134)
    median_blur_size = 9
    iterations = 5

    # Convert image on HSV representation
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Apply a median blur on the image
    hsv_image = cv2.medianBlur(hsv_image, ksize=median_blur_size)

    # Threshold the image with HSV min and max value
    bin_img = phm_img.threshold_hsv(hsv_image, hsv_min, hsv_max)
    # dilate and erode the image to remove possible noise
    bin_img = phm_img.dilate_erode(bin_img, kernel_shape=(3, 3),
                                   iterations=iterations)

    return bin_img


def binarize(raw_images):

    # Compute the mean image of the side view image
    mean_img = phm_img.mean_image(raw_images['side'].values())

    routine_binarization = {
        'side': lambda im: routine_side_binarization(im, mean_img),
        'top': lambda im: routine_top_binarization(im)}

    bin_images = collections.defaultdict(dict)
    for id_camera in raw_images:
        for angle in raw_images[id_camera]:
            bin_images[id_camera][angle] = routine_binarization[id_camera](
                raw_images[id_camera][angle])

    return bin_images


def show_images(images, id_camera="side", angles="[0, 30, 60]"):
    images = [images[id_camera][angle] for angle in eval(angles)]
    phm_display.show_images(images)


# ==============================================================================
# ROUTINE MVR
# ==============================================================================

def routine_select_ref_angle(bin_side_images):
    max_len = 0
    max_angle = None

    for angle in bin_side_images:

        x_pos, y_pos, x_len, y_len = cv2.boundingRect(
            cv2.findNonZero(bin_side_images[angle]))

        if x_len > max_len:
            max_len = x_len
            max_angle = angle

    return max_angle


def get_side_image_projection_list(bin_images, calibrations):

    side_image_projection = list()
    id_camera = "side"
    for angle in bin_images["side"]:
            projection = calibrations[id_camera].get_projection(angle)
            image = bin_images[id_camera][angle]
            side_image_projection.append((image, projection))

    return side_image_projection


def get_image_views(bin_images, calibrations, with_ref_view=True):

    refs_angle_list = list()
    if with_ref_view:
        refs_angle_list = [routine_select_ref_angle(bin_images["side"])]

    image_views = list()
    for id_camera in bin_images:
        for angle in bin_images[id_camera]:
            projection = calibrations[id_camera].get_projection(angle)

            image_ref = None
            if id_camera == "side" and angle in refs_angle_list:
                image_ref = bin_images[id_camera][angle]

            inclusive = False
            if id_camera == "top":
                inclusive = True

            image_views.append(phm_obj.ImageView(
                bin_images[id_camera][angle],
                projection,
                inclusive=inclusive,
                image_ref=image_ref))

    return image_views

# ==============================================================================
# ROUTINE MVR
# ==============================================================================


def show_mesh(vertices_faces,
              color=(0.1, 0.8, 0.1),
              colors=None,
              windows_size=(600, 800),
              screenshot_filename=None,
              screenshot_magnification=10,
              record_filename=None,
              record_quality=2,
              record_rate=25):

    vertices, faces = vertices_faces
    phm_display.show_mesh(vertices,
                          faces,
                          color=color,
                          colors=colors,
                          windows_size=windows_size,
                          screenshot_filename=screenshot_filename,
                          screenshot_magnification=screenshot_magnification,
                          record_filename=record_filename,
                          record_quality=record_quality,
                          record_rate=record_rate)
