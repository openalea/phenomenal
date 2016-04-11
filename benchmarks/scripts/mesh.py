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

voxel_size = 4
voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(
    voxel_size=voxel_size)

vertices, faces = alinea.phenomenal.mesh.meshing(
    voxel_centers, voxel_size,
    reduction=1.0, smoothing_iteration=0, verbose=True)

# # Write
# alinea.phenomenal.misc.write_mesh(
#     vertices, faces, 'mesh_voxel_size_' + str(voxel_size))
#
# # Read
# vertices, faces = alinea.phenomenal.misc.read_mesh(
#     'mesh_voxel_size_' + str(voxel_size))

# normals = alinea.phenomenal.mesh.compute_normal(vertices, faces)
# centers = alinea.phenomenal.mesh.center_of_vertices(vertices, faces)
#
# alinea.phenomenal.viewer.show_mesh(vertices, faces,
#                                    normals=normals, centers=centers)
#
import mayavi
import mayavi.mlab

mayavi.mlab.figure()
mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

mayavi.mlab.triangular_mesh([vert[0] for vert in vertices],
                            [vert[1] for vert in vertices],
                            [vert[2] for vert in vertices],
                            faces)

alinea.phenomenal.viewer.plot_points_3d(voxel_centers,
                                        scale_factor=voxel_size / 2)

mayavi.mlab.show()