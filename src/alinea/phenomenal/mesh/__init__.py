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
====
Mesh
====

.. currentmodule:: alinea.phenomenal.mesh

Sub-package for objects used in mesh.

Algorithms
==========

.. automodule:: alinea.phenomenal.mesh.algorithms
.. currentmodule:: alinea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   meshing
   marching_cubes
   smoothing
   decimation

Formats
=======

.. automodule:: alinea.phenomenal.mesh.formats
.. currentmodule:: alinea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   write_vertices_faces_to_ply_file
   write_vtk_poly_data_to_ply_file
   write_vertices_faces_to_json_file
   read_json_file_to_vertices_faces

Routines
========

.. automodule:: alinea.phenomenal.mesh.routines
.. currentmodule:: alinea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   normals
   centers


VTK Transformation
==================

.. automodule:: alinea.phenomenal.mesh.vtk_transformation
.. currentmodule:: alinea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   from_vertices_faces_to_vtk_poly_data
   from_vtk_poly_data_to_vertices_faces
   from_voxel_centers_to_vtk_image_data
    from_numpy_matrix_to_vtk_image_data

"""

from .algorithms import *
from .formats import *
from .routines import *
from .vtk_transformation import *
