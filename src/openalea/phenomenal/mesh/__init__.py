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
====
Mesh
====

.. currentmodule:: openalea.phenomenal.mesh

Algorithms
==========
.. autosummary::
   :toctree: generated/

   algorithms.meshing
   algorithms.marching_cubes
   algorithms.smoothing
   algorithms.decimation

Formats
=======
.. autosummary::
   :toctree: generated/

   write_vertices_faces_to_ply_file
   write_vtk_poly_data_to_ply_file
   write_vertices_faces_to_json_file
   read_json_file_to_vertices_faces

Routines
========
.. autosummary::
   :toctree: generated/

   normals
   centers


VTK Transformation
==================
.. autosummary::
   :toctree: generated/

   from_vertices_faces_to_vtk_poly_data
   from_vtk_poly_data_to_vertices_faces
   from_voxel_centers_to_vtk_image_data
   from_numpy_matrix_to_vtk_image_data

"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .algorithms import *
from .formats import *
from .routines import *
from .vtk_transformation import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]