# -*- python -*-
#
#       test_config: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 
import csv
import os
import cv2
import numpy
import sys

#       =======================================================================
#       Local Import

import alinea.phenomenal
import alinea.phenomenal.configuration as config
from openalea.deploy.shared_data import shared_data


#       =======================================================================

def write_csv_dict_key_list(csv_name, dictionary):
    with open(csv_name, 'w') as csv_file:
        fieldnames = dictionary.keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for key in dictionary.keys():
            for filename in dictionary[key]:
                writer.writerow({key: filename})


def read_csv_dict_key_list(csv_name):
    dictionary = {}
    with open(csv_name) as csv_file:
        reader = csv.DictReader(csv_file)
        init = True
        for row in reader:
            if init:
                for key in row.keys():
                    dictionary[key] = []
                init = False

            for key, value in row.iteritems():
                if value != '':
                    dictionary[key].append(value)
        return dictionary


def check_import_image(genotype_name, plant_id, rewrite=False,):
    dict_dates_images = config.import_images(
        "../../share/data/Structure_filename",
        genotype_name,
        plant_id)

    csv_name = "../../share/refs/test_config/import_image_2" + genotype_name\
               + \
               "_" + plant_id + ".csv"

    if rewrite:
        write_csv_dict_key_list(csv_name, dict_dates_images)
    else:
        dict_refs = read_csv_dict_key_list(csv_name)
        assert cmp(dict_refs, dict_dates_images) == 0


def check_getconfig():
    config_path = "../../share/refs/test_config/config.cfg"
    parser = config.getconfig(config_path)

    dictionary = parser.as_dict()
    shared_directory = str(shared_data(alinea.phenomenal))

    assert dictionary['General']['configdir'] == "SharedData"

    assert dictionary['side']['crop'] == (50, 1680, 275, 1746)

    assert dictionary['top']['crop2'] == (0, 2055, 0, 2453)
    assert dictionary['top']['y1'] == 0
    assert dictionary['top']['y2'] == 500
    assert dictionary['top']['x1'] == 0
    assert dictionary['top']['x2'] == 2453

    assert dictionary['mainbinarization']['hsvmin'] == (30, 11, 0)
    assert dictionary['mainbinarization']['hsvmax'] == (129, 254, 141)
    assert dictionary['mainbinarization']['mask'] == os.path.join(
        shared_directory, "mask-sideview-mainarea-optimized3.png")

    assert dictionary['ROI1']['hsvmin'] == (19, 39, 0)
    assert dictionary['ROI1']['hsvmax'] == (104, 255, 132)
    assert dictionary['ROI1']['mask'] == os.path.join(
        shared_directory, "masksideview-orange_optimized2.png")
    assert dictionary['ROI1']['background'] == os.path.join(
        shared_directory, "MICHAEL_SIDE_0_20140403.png")

    assert dictionary['ROI2']['hsvmin'] == (14, 36, 0)
    assert dictionary['ROI2']['hsvmax'] == (88, 254, 88)
    assert dictionary['ROI2']['mask'] == os.path.join(
        shared_directory, "mask-sideview-pot-optimized2.png")

    assert dictionary['TOPview']['background'] == os.path.join(
        shared_directory, "MICHAEL_TOP_20140403.png")

    assert dictionary['TOPview']['hsvmin'] == (42, 75, 28)
    assert dictionary['TOPview']['hsvmax'] == (80, 250, 134)
    assert dictionary['TOPview']['mask'] == os.path.join(
        shared_directory, "mask-Orangeband-empty.png")


def check_sidebinarisation_configuration():
    def read_ref_crop(image_path, flag=cv2.CV_LOAD_IMAGE_GRAYSCALE):
        image = cv2.imread(os.path.join(shared_directory, image_path), flag)
        return image[50:1680, 275:1746]

    config_path = "../../share/refs/test_config/config.cfg"
    parser = config.getconfig(config_path)
    configuration = config.sidebinarisation_configuration(parser)
    shared_directory = str(shared_data(alinea.phenomenal))

    # Crop_domain
    assert configuration[0]['y1'] == 50
    assert configuration[0]['y2'] == 1680
    assert configuration[0]['x1'] == 275
    assert configuration[0]['x2'] == 1746

    # Main_optimizer_options
    assert configuration[1]['hsvmin'] == (30, 11, 0)
    assert configuration[1]['hsvmax'] == (129, 254, 141)
    assert numpy.array_equal(configuration[1]['mask'],
                             read_ref_crop(
                                 'mask-sideview-mainarea-optimized3.png'))

    # Band_optimizer_options
    assert configuration[2]['hsvmin'] == (19, 39, 0)
    assert configuration[2]['hsvmax'] == (104, 255, 132)
    assert numpy.array_equal(configuration[2]['mask'],
                             read_ref_crop(
                                 'masksideview-orange_optimized2.png'))
    assert numpy.array_equal(configuration[2]['background'],
                             read_ref_crop('MICHAEL_SIDE_0_20140403.png',
                                           cv2.CV_LOAD_IMAGE_UNCHANGED))
    # pot_optimizer_options
    assert configuration[3]['hsvmin'] == (14, 36, 0)
    assert configuration[3]['hsvmax'] == (88, 254, 88)
    assert numpy.array_equal(configuration[3]['mask'],
                             read_ref_crop('mask-sideview-pot-optimized2.png'))


def test_suite():
    def print_check(string):
        sys.stdout.write('\n' + string + ' : ')
        sys.stdout.flush()

    print "\n================================================================="
    print "test_config.py"
    print "================================================================="

    print_check(check_import_image.__name__)
    yield (check_import_image, "A310", "1580")
    yield (check_import_image, "A310", "1828")
    yield (check_import_image, "A347", "1077")
    yield (check_import_image, "A310", "962")
    yield (check_import_image, "A310", "0962")

    print_check(check_getconfig.__name__)
    yield (check_getconfig.__name__)

    print_check(check_sidebinarisation_configuration.__name__)
    yield (check_sidebinarisation_configuration)
