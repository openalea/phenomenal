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
from alinea.phenomenal.data_access.plant_1 import (
    plant_1_voxels_size_4_without_loss_120)

from alinea.phenomenal.mesh import meshing
from alinea.phenomenal.display import (
    DisplayVoxelGrid)

# ==============================================================================


def main():

    vpc = plant_1_voxels_size_4_without_loss_120()

    DisplayVoxelGrid().show(vpc)

    # show_voxel_point_cloud(vpc,
    #                        # size=(5000, 5000),
    #                        color=(0.1, 0.9, 0.1),
    #                        azimuth=310,
    #                        distance=3000,
    #                        elevation=90,
    #                        focalpoint=(0, 0, 0))

    image_3d = vpc.to_image_3d()

    vertices, faces = meshing(image_3d,
                              reduction=1,
                              smoothing_iteration=10,
                              verbose=True)
    import alinea.phenomenal.mesh.formats as f

    f.write_vertices_faces_to_ply_file('test.ply', vertices, list())


    print("Number of vertices : {nb_vertices}".format(
        nb_vertices=len(vertices)))

    print("Number of faces : {nb_faces}".format(
        nb_faces=len(faces)))

    # show_mesh(vertices, faces,
    #           representation="surface",
    #           size=(5000, 5000),
    #           color=(0.1, 0.9, 0.1),
    #           azimuth=120,
    #           distance=3000,
    #           elevation=90,
    #           focalpoint=(0, 0, 0))

if __name__ == "__main__":
    main()