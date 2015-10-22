# -*- python -*-
#
#       example_calibration_opencv.py :
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
import cv2

#       ========================================================================
#       Local Import
import alinea.phenomenal.calibration_opencv
import alinea.phenomenal.chessboard
import alinea.phenomenal.calibration_tools

#       ========================================================================
#       Code


def example_calibration(data_directory, calib_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_GRAYSCALE)

    chessboard = alinea.phenomenal.chessboard.Chessboard(47, 8, 6)

    calibration = alinea.phenomenal.calibration_opencv.Calibration()
    calibration.calibrate(images, chessboard)

    calibration.print_value()
    alinea.phenomenal.calibration_tools.plot_vectors(
        calibration.rotation_vectors)
    alinea.phenomenal.calibration_tools.plot_vectors(
        calibration.translation_vectors)

    calibration.write_calibration(calib_name)


def example_compute_rotation_and_translation_vectors(calibration_name):
    my_calibration = alinea.phenomenal.calibration_opencv.Calibration.\
        read_calibration(calibration_name)

    my_calibration.print_value()

    angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]

    alinea.phenomenal.calibration_tools.compute_rotation_vectors(
        my_calibration.rotation_vectors, angles)

    alinea.phenomenal.calibration_tools.compute_translation_vectors(
        my_calibration.translation_vectors, angles)

    my_calibration.write_calibration(calibration_name)

    alinea.phenomenal.calibration_tools.plot_vectors(
        my_calibration.translation_vectors)

    alinea.phenomenal.calibration_tools.plot_vectors(
        my_calibration.rotation_vectors)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    example_calibration('../../local/CHESSBOARD/', 'example_calibration_opencv')

    example_compute_rotation_and_translation_vectors(
        'example_calibration_opencv')
