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
=====================
Acces to plant's data
=====================

.. currentmodule:: openalea.phenomenal.data

.. autosummary::
   :toctree: generated/

   path_bin_images
   path_raw_images
   path_chessboard_images
   raw_images
   bin_images
   chessboard_images
   chessboards
   calibrations
   voxel_grid
   tutorial_data_binarization_mask

Synthetic data (for test)
=========================
.. autosummary::
   :toctree: generated/

   bin_images_with_circle
   build_cube
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .synthetic_data import *
from .data import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
