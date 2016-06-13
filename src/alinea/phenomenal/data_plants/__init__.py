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
===========
Data Plants
===========

.. currentmodule:: alinea.phenomenal.data_plants

Sub-package for objects used in data_plants.

Data Creation
===============

.. automodule:: alinea.phenomenal.data_plants.data_creation
.. currentmodule:: alinea.phenomenal.data_plants

.. autosummary::
   :toctree: generated/

   write_circle_on_image
   build_images_1
   build_object_1


Plant 1
=======

.. automodule:: alinea.phenomenal.data_plants.plant_1
.. currentmodule:: alinea.phenomenal.data_plants

.. autosummary::
   :toctree: generated/

   plant_1_images
   plant_1_images_chessboard
   plant_1_images_binarize
   plant_1_mask_mean_shift
   plant_1_mask_hsv
   plant_1_mask_clean_noise
   plant_1_mask_adaptive_threshold
   plant_1_mask_elcom_mean_shift
   plant_1_mask_elcom_hsv
   plant_1_mask_hsv_roi_main
   plant_1_mask_hsv_roi_band
   plant_1_mask_hsv_roi_pot
   plant_1_background_hsv
   plant_1_chessboards
   plant_1_calibration_camera_side
   plant_1_calibration_camera_top
   plant_1_params_camera_opencv_path
   plant_1_voxel_centers

"""

from .data_creation import *
from .plant_1 import *
