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

   chessboard

Calibration
===========
.. autosummary::
   :toctree: generated/

   calibration
   calibration_manual
   calibration_opencv

Frame
=====
.. autosummary::
   :toctree: generated/

    frame

Transformations
================
.. autosummary::
   :toctree: generated/

    transformations
"""

# ==============================================================================


from .calibration import *
from .object import *
from .calibration_manual import *
from .calibration_opencv import *
from .chessboard import *
from .frame import *
from .transformations import *

# ==============================================================================
__all__ = [s for s in dir() if not s.startswith("_")]
