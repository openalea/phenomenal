# -*- python -*-
#
#       calibration.py : 
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
import abc

#       ========================================================================
#       Local Import 

#       ========================================================================
#       Code


class Calibration(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def project_point(self, point, angle):
        pass

    @abc.abstractmethod
    def write_calibration(self, filename):
        pass

    @staticmethod
    @abc.abstractmethod
    def read_calibration(filename):
        pass

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
