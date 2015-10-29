# -*- python -*-
# -*- coding:utf-8 -*-
#
#       configuration.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
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
import os
import glob
import ConfigParser
import cv2

#       ========================================================================
#       Local Import

import openalea.deploy.shared_data
import alinea.phenomenal
import alinea.phenomenal.binarization_factor


#       ========================================================================

def convert_value(value):
        try:
            v = int(value)
        except ValueError:
            if value.startswith('('):
                v = tuple(map(int, value.split('(')[1].split(')')[0].split(',')))
            else:
                v = value
        return v


def load_configuration_file(file_name, file_is_in_share_directory=True):

    share_data_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)
    #~ share_data_directory = "/opt/openalea_dvpt/phenomenal/share/data"
    parser = ConfigParser.ConfigParser()

    if file_is_in_share_directory is True:
        parser.read(share_data_directory / file_name)
        #~ parser.read(os.path.join(share_data_directory, file_name))
    else:
        parser.read(file_name)

    dict_config = dict()
    for sect in parser.sections():

            if sect not in dict_config:
                dict_config[sect] = dict()

            for it in parser.items(sect):
                dict_config[sect][it[0]] = convert_value(it[1])

    for key in dict_config:
        for sub_key in dict_config[key]:
            if str(sub_key).startswith('mask'):
                dict_config[key][sub_key] = cv2.imread(
                    share_data_directory / str(dict_config[key][sub_key]),
                    #~ os.path.join(share_data_directory, str(dict_config[key][sub_key])),
                    cv2.IMREAD_GRAYSCALE)

            if str(sub_key).startswith('background'):
                dict_config[key][sub_key] = cv2.imread(
                    share_data_directory / str(dict_config[key][sub_key]),
                    cv2.IMREAD_COLOR)

    return dict_config


def binarization_factor(file_name, file_is_in_share_directory=True):

    dict_config = load_configuration_file(file_name, file_is_in_share_directory)

    factor = alinea.phenomenal.binarization_factor.BinarizationFactor()
    factor.fill_config(dict_config)

    return factor

def binarization_factor_free(file_name, file_is_in_share_directory=True):
    dict_config = load_configuration_file(file_name, file_is_in_share_directory)
    factor = alinea.phenomenal.binarization_factor.BinarizationFactorFree()
    factor.fill_config(dict_config)

    return factor
    
def import_images(image_directory, genotype_name, plant_id):
    """
    Return a dictionary of side images according to the structure of
    image_directory.

    key is a date
    value is a list of path images

    Structure required :
        image_directory/genotype_name/plant_id*sv*.png

    :param image_directory: The root image directory
    :param genotype_name: String of genotype name
    :param plant_id: String of id of plant
    :return:Dict dates: image for the images matching plant_id in the
    genotype image collection
    """

    im_dir = os.path.join(image_directory, genotype_name, plant_id)
    side_views = glob.glob(im_dir + '*sv*.png')
    dates = map(lambda s: os.path.basename(s).split(' ')[0].split('_')[-1],
                side_views)
    images = {d: [] for d in set(dates)}
    for i, d in enumerate(dates):
        images[d].append(side_views[i])

    return images
