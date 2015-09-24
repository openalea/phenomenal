# -*- python -*-
#
#       example_calibration_jerome.py : 
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
import pickle
import glob
import cv2


#       ========================================================================
#       Local Import
from alinea.phenomenal.chessboard import Chessboard
from alinea.phenomenal.calibration_jerome import Calibration

#       ========================================================================
#       Code


def example_calibration(data_directory, pickle_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_GRAYSCALE)

    chessboard = Chessboard(47, 8, 6)

    # print " find chessboard pts on each image"
    # cv_pts = {}
    # for alpha, img in images.items():
    #     print alpha
    #     pts = chessboard.find_corners(img)
    #     # pts = cc.find_chessboard_corners(img, chessboard.shape)
    #     if pts is not None:
    #         cv_pts[alpha] = pts[:, 0, :]
    #
    # with open("buffer.pkl", 'wb') as f:
    #     pickle.dump(cv_pts, f)

    with open("buffer.pkl", 'rb') as f:
        cv_pts = pickle.load(f)

    with open("initial guess.pkl", 'rb') as f:
        guess = list(pickle.load(f))

    # cc.plot_calibration(chessboard, cv_pts, guess, 48)
    cal = Calibration()
    cal.find_model_parameters(chessboard, cv_pts, guess)

    # cal.print_value()
    cal.write_calibration(pickle_name)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    example_calibration('../../local/data/CHESSBOARD/',
                        'fitted_result')
