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


def test_read_pointcloud_ignores_other_columns(tmp_path):
    filename = tmp_path / "cloud.pts"
    filename.write_text("1.5 2 3 115 115 59\n4 5 6.5 111 116 53\n")
    numpy.testing.assert_array_equal(
        phm_obj.read_pointcloud(filename), [[1.5, 2, 3], [4, 5, 6.5]]
    )


def test_read_pointcloud_single_point(tmp_path):
    filename = tmp_path / "cloud.xyz"
    filename.write_text("1 2 3\n")
    numpy.testing.assert_array_equal(phm_obj.read_pointcloud(filename), [[1, 2, 3]])
