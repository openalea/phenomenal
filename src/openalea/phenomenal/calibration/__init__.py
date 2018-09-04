# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
===========
Calibration
===========

.. currentmodule:: openalea.phenomenal.calibration

Target & Chessboard
===================
.. autosummary::
   :toctree: generated/

   Target
   Chessboard

Calibration
===========
.. autosummary::
   :toctree: generated/

   CalibrationCamera
   CalibrationCameraTop
   CalibrationCameraSideWith2TargetYXZ

Frame
=====
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
from .transformations import *
# ==============================================================================
__all__ = [s for s in dir() if not s.startswith('_')]


