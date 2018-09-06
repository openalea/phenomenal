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
import time

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.segmentation as phm_seg
# import openalea.phenomenal.display as phm_display
# ==============================================================================


plant_number = 2
voxels_size = 8
bin_images = phm_data.bin_images(plant_number=plant_number)
calibrations = phm_data.calibrations(plant_number=plant_number)
voxel_grid = phm_data.voxel_grid(plant_number=plant_number,
                                 voxels_size=voxels_size)

init_start = time.time()
# ==============================================================================

start = time.time()
graph = phm_seg.graph_from_voxel_grid(voxel_grid)
print("time processing , graph_from_voxel_grid : {}".format(time.time() - start))

start = time.time()
voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)
print("time processing , skeletonize : {}".format(time.time() - start))

start = time.time()
image_projection = list()
for angle in range(0, 360, 30):
    projection = calibrations["side"].get_projection(angle)
    image_projection.append((bin_images["side"][angle], projection))
print("time processing , image_projection : {}".format(time.time() - start))

print("len(voxel_skeleton_reduced.segments) : {}".format(
    len(voxel_skeleton.segments)))

start = time.time()
voxel_skeleton_reduced = phm_seg.segment_reduction(
    voxel_skeleton, image_projection,
    required_visible=4,
    nb_min_pixel=100)

print("time processing , segment_reduction : {}".format(time.time() - start))

# len_ref_segments = {2: 14}
print("len(voxel_skeleton_reduced.segments) : {}".format(
    len(voxel_skeleton_reduced.segments)))
# assert (len_ref_segments[2] == len(voxel_skeleton_reduced.segments))

# import openalea.phenomenal.display as phm_display
# ds = phm_display.DisplaySkeleton()
# ds(voxel_skeleton_reduced)

start = time.time()
vms = phm_seg.maize_segmentation(voxel_skeleton, graph)
print("time processing , maize_segmentation : {}".format(time.time() - start))

start = time.time()
vmsi = phm_seg.maize_analysis(vms)
print("time processing , maize_analysis : {}".format(time.time() - start))
# ==============================================================================
print("time processing , ALL : {}".format(time.time() - init_start))

# Profilage


def test():
    voxel_skeleton_reduced = phm_seg.segment_reduction(
        voxel_skeleton, image_projection,
        required_visible=4,
        nb_min_pixel=100)

import cProfile
cProfile.run("test()", sort="cumulative")
