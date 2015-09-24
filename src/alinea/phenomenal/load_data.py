# -*- python -*-
#
#       load._data.py : Function for load data in visualea
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
import cv2


#       ========================================================================
#       Local Import 
from openalea.deploy.shared_data import shared_data
import alinea.phenomenal


#       ========================================================================


def side_blob_test_1():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'side_blob_test_1.png')


def side_blob_test_2():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'side_blob_test_2.png')


def side_blob_test_3():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'side_blob_test_3.png')


def side_blob_test_4():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'side_blob_test_4.png')


def top_blob_test():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'top_blob_test.png')


def top_blob_test():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'top_blob_test.png')


def illumination_test_image_1():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_1.png')


def illumination_test_image_2():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_2.png')


def illumination_test_image_3():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_3.png')


def illumination_test_image_4():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_4.png')


def illumination_test_image_5():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_5.png')


def illumination_test_image_6():
    shared_directory = shared_data(alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' +
                      'illumination_test_image_6.png')