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

.. currentmodule:: alinea.phenomenal.display

Sub-package for objects used in display.

Image
=====

.. automodule:: alinea.phenomenal.display.image
.. currentmodule:: alinea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_image
   show_images

Calibration
===========

.. automodule:: alinea.phenomenal.display.calibration
.. currentmodule:: alinea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_image_with_chessboard_corners
   show_chessboard_3d_projection_on_image


Mesh
====

.. automodule:: alinea.phenomenal.display.mesh
.. currentmodule:: alinea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_mesh
   show_poly_data

Octree
======

.. automodule:: alinea.phenomenal.display.octree
.. currentmodule:: alinea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_octree
   show_each_stage_of_octree

Multi_view_reconstruction
=========================

.. automodule:: alinea.phenomenal.display.multi_view_reconstruction
.. currentmodule:: alinea.phenomenal.display

.. autosummary::
   :toctree: generated/

   show_points_3d
   plot_points_3d
   plot_3d

"""

from alinea.phenomenal.display.image import (
    show_image,
    show_images)

from alinea.phenomenal.display.calibration import (
    show_chessboard_3d_projection_on_image,
    show_image_with_chessboard_corners)

from alinea.phenomenal.display.multi_view_reconstruction import (
    plot_3d,
    plot_points_3d,
    show_points_3d)

from alinea.phenomenal.display.octree import (
    show_octree,
    show_each_stage_of_octree)

from alinea.phenomenal.display.mesh import (
    show_mesh,
    show_poly_data)
