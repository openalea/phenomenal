# -*- python -*-
#
#       phenomenal_config: Module Description
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
#       =======================================================================

__revision__ = ""

#       =======================================================================
#       External Import
import os
import cv2
from glob import glob
from ConfigParser import ConfigParser
from collections import OrderedDict


#       =======================================================================
#       Local Import
from openalea.deploy.shared_data import shared_data
import alinea.phenomenal
import alinea.phenomenal.binarization_configuration as b_config


#       =======================================================================


class PhenomenalConfigParser(ConfigParser, object):
    """Initialisation class necessary to read all the data from config.cfg
    necessary for binarization and segmentation
    """

    def _convert(self, value):
        try:
            v = int(value)
        except ValueError:
            if value.startswith('('):
                v = tuple(map(int,
                              value.split('(')[1].split(')')[0].split(',')))
            else:
                v = value
        return v

    def read(self, filenames):
        # Call to read method of ConfigParser
        super(PhenomenalConfigParser, self).read(filenames)
        for sect in self.sections():
            for it in self.items(sect):
                self.set(sect, it[0], self._convert(it[1]))

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


def loadconfig(config='SideCamera2013_ZoomOut.cfg'):
    """ load a configuration from shared data directory
    """
    confdir = shared_data(alinea.phenomenal)
    p = PhenomenalConfigParser()
    p.read(confdir / config)
    d = p.as_dict()
    if p.has_section('config_images'):
        for it in p.items('config_images', raw=True):
            flag = cv2.IMREAD_UNCHANGED
            if it[1].endswith('mask'):
                flag = cv2.IMREAD_GRAYSCALE
            d['config_images'][it[0]] = cv2.imread(confdir / it[1], flag)

    if p.has_section('config_images_elcom'):
        for it in p.items('config_images_elcom', raw=True):
            flag = cv2.IMREAD_UNCHANGED
            if it[1].endswith('mask'):
                flag = cv2.IMREAD_GRAYSCALE
            d['config_images_elcom'][it[0]] = cv2.imread(confdir / it[1], flag)

    for key in d:
        for sub_key in d[key]:
            if str(sub_key).startswith('mask'):
                d[key][sub_key] = cv2.imread(confdir / str(d[key][sub_key]),
                                             cv2.IMREAD_GRAYSCALE)

            if str(sub_key).startswith('background'):
                d[key][sub_key] = cv2.imread(confdir / str(d[key][sub_key]),
                                             cv2.IMREAD_UNCHANGED)
    return d


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
    side_views = glob(im_dir + '*sv*.png')
    dates = map(lambda s: os.path.basename(s).split(' ')[0].split('_')[-1],
                side_views)
    images = {d: [] for d in set(dates)}
    for i, d in enumerate(dates):
        images[d].append(side_views[i])

    return images


# backward compatibility functions
def getconfig(configfile=None):
    if configfile is None:
        configfile = shared_data(alinea.phenomenal) / 'config.cfg'

    p = PhenomenalConfigParser()
    p.read(configfile)

    if p.has_option('General', 'configdir'):
        confdir = p.get('General', 'configdir')
        if confdir == 'SharedData':
            confdir = str(shared_data(alinea.phenomenal))
        for s in p._sections:
            for it in p.items(s, raw=True):
                if it[0] == 'mask' or it[0] == 'background':
                    p.set(s, it[0],
                          os.path.join(confdir, os.path.basename(it[1])))

    if p.has_option('General', 'config_images_dir'):
        confdir = p.get('General', 'config_images_dir')
        if confdir == 'SharedData':
            confdir = str(shared_data(alinea.phenomenal))
        s = 'config_images'
        for it in p.items(s, raw=True):
            p.set(s, it[0], os.path.join(confdir, os.path.basename(it[1])))

    return p


def crop_domain_node(domain):
    return domain['y1'], domain['y2'], domain['x1'], domain['x2']


def config_value(config, dict_name_1, dict_name_2):
    try:
        value = config[dict_name_1][dict_name_2]
    except KeyError:
        value = None
    return value


def init_roi_config(roi, config, name):
    roi.hsv_min = config_value(config, name, 'hsv_min')
    roi.hsv_max = config_value(config, name, 'hsv_max')
    roi.mask = config_value(config, name, 'mask')


def binarization_config(config):
    """

    :param config:
    :return:
    """
    b_conf = b_config.BinarizationConfig()

    mbf = b_conf.meanshift_binarization_factor
    mbf.threshold = config_value(config,
                                 'binarization',
                                 'threshold')
    mbf.dark_background = config_value(config,
                                       'binarization',
                                       'dark_background')

    init_roi_config(b_conf.roi_main, config, 'roi_main')
    init_roi_config(b_conf.roi_stem, config, 'roi_stem')
    init_roi_config(b_conf.roi_pot, config, 'roi_pot')
    init_roi_config(b_conf.roi_orange_band, config, 'roi_orange_band')
    init_roi_config(b_conf.roi_panel, config, 'roi_panel')

    b_conf.cubicle_domain = config_value(config, 'General', 'cubicle_domain')
    b_conf.background = config_value(config, 'General', 'background')

    return b_conf


def read_config(config_file):
    p = PhenomenalConfigParser()
    p.read(config_file)
    d = p.as_dict()

    if d['General']['configdir'] == 'SharedData':
        shared_directory = shared_data(alinea.phenomenal)
    else:
        shared_directory = d['General']['configdir']

    for key in d:
        for sub_key in d[key]:
            if str(sub_key).startswith('mask'):
                d[key][sub_key] = cv2.imread(
                    shared_directory / str(d[key][sub_key]),
                    cv2.CV_LOAD_IMAGE_GRAYSCALE)

            if str(sub_key).startswith('background'):
                d[key][sub_key] = cv2.imread(
                    shared_directory / str(d[key][sub_key]),
                    cv2.CV_LOAD_IMAGE_UNCHANGED)
    return d


def sidebinarisation_configuration(config_parser):
    """ configuration of sidebinarisation step"""

    def _read_crop(image_path, domain, flag='CV_LOAD_IMAGE_UNCHANGED'):

        flag = getattr(cv2, flag)
        img = cv2.imread(image_path, flag)
        return img[domain['y1']:domain['y2'], domain['x1']:domain['x2']]

    d = config_parser.as_dict()

    crop_domain = {
        'y1': d['side']['crop'][0],
        'y2': d['side']['crop'][1],
        'x1': d['side']['crop'][2],
        'x2': d['side']['crop'][3]}

    main_optimizer_options = {
        'hsvmin': d['mainbinarization']['hsvmin'],
        'hsvmax': d['mainbinarization']['hsvmax'],
        'mask': _read_crop(d['mainbinarization']['mask'],
                           crop_domain,
                           'CV_LOAD_IMAGE_GRAYSCALE')}

    band_optimizer_options = {
        'hsvmin': d['ROI1']['hsvmin'],
        'hsvmax': d['ROI1']['hsvmax'],
        'mask': _read_crop(d['ROI1']['mask'],
                           crop_domain,
                           'CV_LOAD_IMAGE_GRAYSCALE'),
        'background': _read_crop(d['ROI1']['background'], crop_domain)}

    pot_optimizer_options = {
        'hsvmin': d['ROI2']['hsvmin'],
        'hsvmax': d['ROI2']['hsvmax'],
        'mask': _read_crop(d['ROI2']['mask'],
                           crop_domain,
                           'CV_LOAD_IMAGE_GRAYSCALE')}

    return (crop_domain,
            main_optimizer_options,
            band_optimizer_options,
            pot_optimizer_options)


def topbinarisation_configuration(config_parser):
    """ configuration of sidebinarisation step"""

    def _read_crop(image_path, domain, flag='CV_LOAD_IMAGE_UNCHANGED'):

        flag = getattr(cv2, flag)
        img = cv2.imread(image_path, flag)
        return img[domain['y1']:domain['y2'], domain['x1']:domain['x2']]

    d = config_parser.as_dict()

    main_optimizer_options = {'hsvmin': d['TOPview']['hsvmin'],
                              'hsvmax': d['TOPview']['hsvmax'],
                              'mask': cv2.imread(d['TOPview']['mask'],
                                                 cv2.CV_LOAD_IMAGE_GRAYSCALE)}
    return main_optimizer_options


def topbinarisation_options(config_parser):
    """Define the parameters to be extracted from config.cfg for topbinarisation
    """

    d = config_parser.as_dict()
    opts = OrderedDict([
        ('mainhsvmin', d['TOPview']['hsvmin']),
        ('mainhsvmax', d['TOPview']['hsvmax']),
        ('mainmask', d['TOPview']['mask']),
        ('roi1hsvmin', d['TOPview']['hsvmin']),
        ('roi1hsvmax', d['TOPview']['hsvmax']),
        ('roi1mask', d['TOPview']['mask']),
        ('roi2hsvmin', d['TOPview']['hsvmin']),
        ('roi2hsvmax', d['TOPview']['hsvmax']),
        ('roi2mask', d['TOPview']['mask']),
        ('y1', d['top']['crop2'][0]),
        ('y2', d['top']['crop2'][1]),
        ('x1', d['top']['crop2'][2]),
        ('x2', d['top']['crop2'][3]),
        ('background', d['TOPview']['background'])])
    return opts


def topbinarisation_options_node(configparser):
    opts = topbinarisation_options(configparser)
    # temp
    # del opts['background']
    return opts.values()
