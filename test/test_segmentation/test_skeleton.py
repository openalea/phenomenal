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
from __future__ import division, print_function

import os

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.segmentation as phm_seg
# ==============================================================================

data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "../data/plant_1")

plant_1_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "../data/plant_1")

plant_1_bin__dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "../data/plant_1/bin")


def test_running():

    bin_images = phm_data.bin_images(plant_1_dir)
    calibrations = phm_data.calibrations(plant_1_dir)
    voxel_grid = phm_data.random_voxel_grid(shape=(25, 25, 25),
                                            voxels_size=32)

    # Load images binarize

    graph = phm_seg.graph_from_voxel_grid(voxel_grid)

    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)

    image_projection = list()
    for angle in [0, 120, 270]:
        projection = calibrations["side"].get_projection(angle)
        image_projection.append((bin_images["side"][angle], projection))

    voxel_skeleton = phm_seg.segment_reduction(
        voxel_skeleton, image_projection,
        required_visible=1,
        nb_min_pixel=100)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
