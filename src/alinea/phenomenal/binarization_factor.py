# -*- python -*-
#
#       binarization_factor.py :
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

""" Include definition class for object parameter of binarization """

#       ========================================================================


def dict_config_value(dict_config, key_1, key_2):
        try:
            return dict_config[key_1][key_2]
        except KeyError:
            return None


class RegionOfInterest:
    def __init__(self, dict_config, name):
        self.hsv_min = dict_config_value(dict_config, name, 'hsv_min')
        self.hsv_max = dict_config_value(dict_config, name, 'hsv_max')
        self.mask = dict_config_value(dict_config, name, 'mask')

    def print_value(self):
        print 'hsv_min ', self.hsv_min
        print 'hsv_max ', self.hsv_max
        print 'mask is None :', self.mask is None


class MeanShiftBinarizationFactor(object):
    def __init__(self, dict_config):
        if dict_config is None:
            self._threshold = 0.3
            self._dark_background = False
        else:

            value = dict_config_value(dict_config, 'binarization', 'threshold')

            if value is None:
                self._threshold = 0.3
            else:
                self._threshold = float(value)

            value = dict_config_value(dict_config,
                                      'binarization',
                                      'dark_background')

            if value is None:
                self._dark_background = False
            else:
                self._dark_background = bool(value)

    def print_value(self):
        print 'threshold ', self._threshold
        print 'dark_background ', self._dark_background

    #   =======================================================================
    #   threshold
    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if isinstance(value, type(self._threshold)):
            self._threshold = value

    #   =======================================================================
    #   dark_background
    @property
    def dark_background(self):
        return self._dark_background

    @dark_background.setter
    def dark_background(self, value):
        if isinstance(value, type(self._dark_background)):
            self._dark_background = value


class BinarizationFactor(object):
    def __init__(self):
        #   ===================================================================
        #   Default value
        self.mean_shift_binarization_factor = None
        self.roi_main = None
        self.roi_stem = None
        self.roi_pot = None
        self.roi_panel = None
        self.roi_orange_band = None
        self.cubicle_domain = None
        self.background = None

    def fill_config(self, dict_config):
        self.mean_shift_binarization_factor = \
            MeanShiftBinarizationFactor(dict_config)

        self.roi_main = RegionOfInterest(dict_config, 'roi_main')
        self.roi_stem = RegionOfInterest(dict_config, 'roi_stem')
        self.roi_pot = RegionOfInterest(dict_config, 'roi_pot')
        self.roi_orange_band = RegionOfInterest(dict_config, 'roi_orange_band')
        self.roi_panel = RegionOfInterest(dict_config, 'roi_panel')

        self.cubicle_domain = dict_config_value(dict_config,
                                                'General',
                                                'cubicle_domain')

        self.background = dict_config_value(dict_config,
                                            'General',
                                            'background')

    def print_value(self):

        self.mean_shift_binarization_factor.print_value()

        self.roi_main.print_value()
        self.roi_stem.print_value()
        self.roi_pot.print_value()
        self.roi_panel.print_value()
        self.roi_orange_band.print_value()

        print 'Cubicle domain : ', self.cubicle_domain
        print 'Background is None : ', self.background is None
