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
from alinea.phenomenal.data_access import plant_1_voxel_centers
from alinea.phenomenal.data_structure import voxel_centers_to_image_3d
from alinea.phenomenal.mesh import meshing, centers, normals
from alinea.phenomenal.display import show_mesh, show_points_3d

from alinea.phenomenal.data_structure import VoxelPointCloud
# ==============================================================================

# voxel_size = 4
# voxel_centers = plant_1_voxel_centers(voxel_size=voxel_size)

filename = "4_without_loss.json"
vpc = VoxelPointCloud.read_from_json(filename)
voxels_center = vpc.voxels_center
voxels_size = vpc.voxels_size

show_points_3d(voxels_center, scale_factor=voxels_size, color=(0.1, 0.9, 0.1))


image3d = voxel_centers_to_image_3d(voxels_center, voxels_size)
vertices, faces = meshing(image3d,
                          reduction=1,
                          smoothing_iteration=0,
                          verbose=True)

# # Write
# alinea.phenomenal.misc.write_mesh(
#     vertices, faces, 'mesh_voxel_size_' + str(voxel_size))
#
# # Read
# vertices, faces = alinea.phenomenal.misc.read_mesh(
#     'mesh_voxel_size_' + str(voxel_size))

# norms = normals(vertices, faces)
# cents = centers(vertices, faces)

show_mesh(vertices, faces)#, representation="wireframe")
