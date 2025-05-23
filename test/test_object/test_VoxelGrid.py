# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os
import numpy.random
import openalea.phenomenal.object as phm_obj
# ==============================================================================


def test_read_write():
    voxels_size = 16
    voxels_position = numpy.array(list(numpy.ndindex((10, 15, 5)))) * 16
    src_vg = phm_obj.VoxelGrid(voxels_position, voxels_size)

    for ext in ("npz", "json", "csv", "xyz"):
        filename = "test." + ext
        src_vg.write(filename)
        if ext == "xyz":
            dist_vg = phm_obj.VoxelGrid.read(filename, voxels_size)
        else:
            dist_vg = phm_obj.VoxelGrid.read(filename)
        os.remove(filename)

        assert src_vg.voxels_size == dist_vg.voxels_size
        assert (src_vg.voxels_position == dist_vg.voxels_position).all()
