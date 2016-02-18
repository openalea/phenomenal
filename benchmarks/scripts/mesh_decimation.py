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
import alinea.phenomenal.plant_1
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
import alinea.phenomenal.mesh
import alinea.phenomenal.viewer
# ==============================================================================
voxel_size = 5
voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(
    voxel_size=voxel_size)

matrix, index, origin = alinea.phenomenal.data_transformation.\
    points_3d_to_matrix(voxel_centers, voxel_size)

# ==============================================================================

vertices, faces = alinea.phenomenal.mesh.meshing(matrix, origin, voxel_size)

alinea.phenomenal.viewer.show_mesh(vertices, faces)

poly_data = alinea.phenomenal.mesh.create_poly_data(vertices, faces)

alinea.phenomenal.viewer.show_poly_data(poly_data)

poly_decimated = alinea.phenomenal.mesh.mesh_decimation(
    poly_data, verbose=True)

alinea.phenomenal.viewer.show_poly_data(poly_decimated)

vertices, n_faces = alinea.phenomenal.mesh.create_vertices_faces(poly_decimated)
alinea.phenomenal.viewer.show_mesh(vertices, n_faces)
