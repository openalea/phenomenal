# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
"""
============
Calibration
============

.. currentmodule:: alinea.phenomenal.calibration

Sub-package for objects used in calibration.

Calibration
===========

.. automodule:: alinea.phenomenal.calibration.calibration
.. currentmodule:: alinea.phenomenal.calibration

.. autosummary::
   :toctree: generated/

   CalibrationCamera
   CalibrationCameraTop
   CalibrationCameraSideWith2TargetXYZ

Calibration Manual
==================

.. automodule:: alinea.phenomenal.calibration.calibration_manual
.. currentmodule:: alinea.phenomenal.calibration

.. autosummary::
   :toctree: generated/

   EnvironmentCamera
   Calibration

Calibration OpenCV
==================

.. automodule:: alinea.phenomenal.calibration.calibration_opencv
.. currentmodule:: alinea.phenomenal.calibration

.. autosummary::
   :toctree: generated/

   Calibration

Frame
=====

.. automodule:: alinea.phenomenal.calibration.frame
.. currentmodule:: alinea.phenomenal.calibration

.. autosummary::
   :toctree: generated/

    Frame
    x_axis
    y_axis
    z_axis
"""
# ==============================================================================

from __future__ import division, print_function, absolute_import

from .calibration import *
from .calibration_manual import *
from .calibration_opencv import *
from .chessboard import *
from .frame import *

# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
