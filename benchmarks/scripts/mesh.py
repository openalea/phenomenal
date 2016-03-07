# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
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

voxel_size = 3
voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(
    voxel_size=voxel_size)

vertices, faces = alinea.phenomenal.mesh.meshing(
    voxel_centers, voxel_size, reduction=0.95, smoothing=True, verbose=True)

# Write
alinea.phenomenal.misc.write_mesh(
    vertices, faces, 'mesh_radius_' + str(voxel_size))

# Read
vertices, faces = alinea.phenomenal.misc.read_mesh(
    'mesh_radius_' + str(voxel_size))

normals = alinea.phenomenal.mesh.compute_normal(vertices, faces)
centers = alinea.phenomenal.mesh.center_of_vertices(vertices, faces)

alinea.phenomenal.viewer.show_mesh(vertices, faces,
                                   normals=normals, centers=centers)
