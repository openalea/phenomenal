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
=======
Display
=======

.. currentmodule:: openalea.phenomenal.display

Sub-package for objects used in display.

Image
=====

.. automodule:: openalea.phenomenal.display.image
.. currentmodule:: openalea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_image
   show_images

Calibration
===========

.. automodule:: openalea.phenomenal.display.calibration
.. currentmodule:: openalea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_image_with_chessboard_corners
   show_chessboard_3d_projection_on_image


Mesh
====

.. automodule:: openalea.phenomenal.display.mesh
.. currentmodule:: openalea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_mesh
   show_poly_data

Octree
======

.. automodule:: openalea.phenomenal.display.octree
.. currentmodule:: openalea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_octree
   show_each_stage_of_octree

Multi_view_reconstruction
=========================

.. automodule:: openalea.phenomenal.display.multi_view_reconstruction
.. currentmodule:: openalea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_points_3d
   plot_points_3d
   plot_3d
   show_list_points_3d

"""
# ==============================================================================

from __future__ import division, print_function, absolute_import

from .calibration import *
from .image import *
from .mesh import *
from .peak import *

from .display import *
from .displayVtk import *
from .displayVoxel import *
from .displaySkeleton import *
from .displayVoxelGrid import *
from .displaySegmentation import *

# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
