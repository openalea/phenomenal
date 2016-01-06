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

import types

def dict_factor_value(dict_factor, key_1, key_2):
    try:
        return dict_factor[key_1][key_2]
    except KeyError:
        return None


class RegionOfInterest:
    def __init__(self, dict_config, name):
        self.hsv_min = dict_factor_value(dict_config, name, 'hsv_min')
        self.hsv_max = dict_factor_value(dict_config, name, 'hsv_max')
        self.mask = dict_factor_value(dict_config, name, 'mask')


class MeanShiftBinarizationFactor(object):
    def __init__(self, dict_config):
        if dict_config is None:
            self._threshold = 0.3
            self._dark_background = False
        else:

            value = dict_factor_value(dict_config, 'binarization', 'threshold')

            if value is None:
                self._threshold = 0.3
            else:
                self._threshold = float(value)

            value = dict_factor_value(
                dict_config, 'binarization', 'dark_background')

            if value is None:
                self._dark_background = False
            else:
                self._dark_background = bool(value)

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
        self.mean_shift_binarization_factor = None

        #   ====================================================================
        #   SIDE

        self.side_roi_main = None
        self.side_roi_stem = None
        self.side_roi_pot = None
        self.side_roi_panel = None
        self.side_roi_orange_band = None
        self.side_cubicle_domain = None
        self.side_cubicle_background = None

        #   ====================================================================
        #   TOP

        self.top_cubicle_domain = None
        self.top_cubicle_background = None
        self.top_roi_main = None

    def fill_config(self, dict_factor):
        self.mean_shift_binarization_factor = \
            MeanShiftBinarizationFactor(dict_factor)

        #   ====================================================================
        #   SIDE

        self.side_roi_main = RegionOfInterest(dict_factor, 'side_roi_main')
        self.side_roi_stem = RegionOfInterest(dict_factor, 'side_roi_stem')
        self.side_roi_pot = RegionOfInterest(dict_factor, 'side_roi_pot')
        self.side_roi_panel = RegionOfInterest(dict_factor, 'side_roi_panel')
        self.side_roi_orange_band = RegionOfInterest(
            dict_factor, 'side_roi_orange_band')

        self.side_cubicle_domain = dict_factor_value(
            dict_factor, 'side_cubicle', 'domain')

        self.side_cubicle_background = dict_factor_value(
            dict_factor, 'side_cubicle', 'background')

        #   ====================================================================
        #   TOP

        self.top_cubicle_domain = dict_factor_value(
            dict_factor, 'top_cubicle', 'domain')

        self.top_cubicle_background = dict_factor_value(
            dict_factor, 'top_cubicle', 'background')

        self.top_roi_main = RegionOfInterest(dict_factor, 'top_roi_main')


class BinarizationFactorFree(object):
    def __init__(self, dict_factor=None):
        if dict_factor:
            self.fill_config(dict_factor)

    def fill_config(self, dict_factor):
        for key, value in dict_factor.items():
            if type(value) == types.DictType:
                factor = BinarizationFactorFree()
                factor.fill_config(value)
                setattr(self, key, factor)
            else:
                setattr(self, key, value)
                
