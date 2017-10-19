====
Mesh
====

.. currentmodule:: openalea.phenomenal.mesh

Sub-package for objects used in mesh.

Algorithms
==========

.. automodule:: openalea.phenomenal.mesh.algorithms
.. currentmodule:: openalea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   meshing
   marching_cubes
   smoothing
   decimation

Formats
=======

.. automodule:: openalea.phenomenal.mesh.formats
.. currentmodule:: openalea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   write_vertices_faces_to_ply_file
   write_vtk_poly_data_to_ply_file
   write_vertices_faces_to_json_file
   read_json_file_to_vertices_faces

Routines
========

.. automodule:: openalea.phenomenal.mesh.routines
.. currentmodule:: openalea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   normals
   centers


VTK Transformation
==================

.. automodule:: openalea.phenomenal.mesh.vtk_transformation
.. currentmodule:: openalea.phenomenal.mesh

.. autosummary::
   :toctree: generated/

   from_vertices_faces_to_vtk_poly_data
   from_vtk_poly_data_to_vertices_faces
   from_voxel_centers_to_vtk_image_data
    from_numpy_matrix_to_vtk_image_data