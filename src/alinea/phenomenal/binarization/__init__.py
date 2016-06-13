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
Binarization
============

.. currentmodule:: alinea.phenomenal.binarization

Sub-package for objects used in binarization.

Threshold
=========

.. autosummary::
   :toctree: generated/

   meanshift
   hsv

Morphology
==========

.. autosummary::
   :toctree: generated/

   dilate_erode
   erode_dilate
   close

Routines
========

.. autosummary::
   :toctree: generated/

   mean
   hsv

Formats
=======

.. autosummary::
   :toctree: generated/

    read_image
    write_image

"""

from .formats import *
from .morphology import *
from .routines import *
from .threshold import *
