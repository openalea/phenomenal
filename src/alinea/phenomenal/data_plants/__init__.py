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
   plant_1_images_binarize
   plant_1_chessboards
   plant_1_calibration_camera_side
   plant_1_calibration_camera_top
   plant_1_voxel_centers

"""

from alinea.phenomenal.data_plants.data_creation import (
    build_images_1,
    build_object_1,
    write_circle_on_image)

from alinea.phenomenal.data_plants.plant_1 import (
    plant_1_images,
    plant_1_images_binarize,
    plant_1_chessboards,
    plant_1_calibration_camera_side,
    plant_1_calibration_camera_top,
    plant_1_voxel_centers)

