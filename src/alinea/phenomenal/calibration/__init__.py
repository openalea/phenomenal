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
   CalibrationCameraTopNew
   CalibrationCameraTop
   CalibrationCameraSideWith1Target
   CalibrationCameraSideWith2Target

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

Transformations
===============

.. automodule:: alinea.phenomenal.calibration.transformations
.. currentmodule:: alinea.phenomenal.calibration

"""

from .calibration import *
from .calibration_manual import *
from .calibration_opencv import *
from .chessboard import *
from .frame import *
