# -*- python -*-
#
#       script_validation.py : 
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       ========================================================================

#       ========================================================================
#       External Import
import glob
import random
import matplotlib.pyplot
import numpy
import cv2
import json

import alinea.phenomenal.chessboard

#       ========================================================================
#       Code
#       ========================================================================
#       Local Import


def load_chessboard(data_directory, nb_image):
    import alinea.phenomenal.chessboard

    # Load files
    files_path = glob.glob(data_directory + '*.png')
    angles = map(
        lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_path)

    image_path = dict()
    for i in range(len(files_path)):
        image_path[angles[i]] = files_path[i]

    # Define Chessboard size
    chessboard = alinea.phenomenal.chessboard.Chessboard(47, (8, 6))

    # Load image and find chessboard corners in each image
    choose_angles = random.sample(image_path.keys(), nb_image)
    for angle in choose_angles:
        print 'CHESSBOARD : ', data_directory, ' ', angle
        img = cv2.imread(image_path[angle], cv2.IMREAD_GRAYSCALE)
        chessboard.find_and_add_corners(angle, img)

    return chessboard, choose_angles

#   ========================================================================
#   CHESSBOARD Ref

chessboard_ref_1 = alinea.phenomenal.chessboard.Chessboard.read(
    './chessboard/chessboard_1')

chessboard_ref_2 = alinea.phenomenal.chessboard.Chessboard.read(
    './chessboard/chessboard_2')


def compute_error(nb_image):
    import alinea.phenomenal.chessboard

    #   ========================================================================
    #   CHESSBOARD Sampling

    chessboard_1, angles_1 = load_chessboard('../../local/CHESSBOARD_1/',
                                             nb_image)

    chessboard_2, angles_2 = load_chessboard('../../local/CHESSBOARD_2/',
                                             nb_image)

    # ==========================================================================
    # Calibration
    import alinea.phenomenal.calibration_model

    # Create Object
    calibration = alinea.phenomenal.calibration_model.Calibration(
        [chessboard_1, chessboard_2], (2056, 2454), verbose=True)

    # Do Calibration
    res = calibration.find_model_parameters(number_of_repetition=5)
    cam_params, chess_params = res

    err = alinea.phenomenal.calibration_model.compute_error_projection(
        cam_params, [chessboard_ref_1, chessboard_ref_2], chess_params)

    print err
    return err


def launch_computation(nb_image, repetition):
    err = list()
    for i in range(repetition):
        err.append(compute_error(nb_image))

    return err


def launch_validation(repetition, max_image):
    result = dict()
    for nb_image in range(1, max_image + 1, 1):
        err = list()
        for i in range(repetition):
            err.append(compute_error(nb_image))
        result[nb_image] = err
    return result


def viewing(result):
    for nb_image in result:
        len_rep = float(len(result[nb_image]))
        rep = numpy.ones((len_rep, )) * float(nb_image)
        matplotlib.pyplot.plot(rep, result[nb_image], 'ro')
    matplotlib.pyplot.show()


def write_result(file_path, result):
    with open(file_path + '.json', 'w') as output_file:
        json.dump(result, output_file)


def read_result(file_path):
    with open(file_path + '.json', 'r') as input_file:
        result = json.load(input_file)
    return result

if __name__ == "__main__":

    repetition = 4
    max_image = 38
    validation_result = launch_validation(repetition, max_image)

    write_result('validation_result', validation_result)

    validation_result = read_result('validation_result')
    viewing(validation_result)
