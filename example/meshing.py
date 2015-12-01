# -*- python -*-
#
#       meshing.py : 
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

import alinea.phenomenal.data_load
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
import alinea.phenomenal.mesh
import alinea.phenomenal.viewer

# ==============================================================================

radius = 2

points_3d_path = alinea.phenomenal.data_load.test_plant_1_points_3d_path(
    radius=radius)

points_3d = alinea.phenomenal.misc.read_xyz(points_3d_path)

matrix, index, origin = alinea.phenomenal.data_transformation.\
    points_3d_to_matrix(points_3d, radius)

vertices, faces = alinea.phenomenal.mesh.meshing(matrix, origin, radius)

# Write
alinea.phenomenal.misc.write_mesh(vertices, faces, 'mesh_radius_' + str(radius))

# Read
vertices, faces = alinea.phenomenal.misc.read_mesh('mesh_radius_' + str(radius))

normals = alinea.phenomenal.mesh.compute_normal(vertices, faces)
centers = alinea.phenomenal.mesh.center_of_vertices(vertices, faces)

alinea.phenomenal.viewer.show_mesh(
    vertices, faces, normals=normals, centers=centers)

