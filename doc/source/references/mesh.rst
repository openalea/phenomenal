====
Mesh
====

.. currentmodule:: openalea.phenomenal.mesh
.. automodule:: openalea.phenomenal.mesh

Algorithms
==========
.. autosummary::
   :toctree: generated/

   meshing
   marching_cubes
   smoothing
   decimation

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