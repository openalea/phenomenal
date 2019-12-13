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
from random import randrange
import numpy
import numpy.random

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.segmentation as phm_seg
import openalea.phenomenal.object as phm_obj

# ==============================================================================


def _generate_random_segment():
    return phm_obj.VoxelSegment(numpy.random.random(size=(10, 3)),
                                numpy.random.random(size=(100, 3)),
                                numpy.random.random(size=(50, 3)))


def _generate_random_orange(label):

    vo = phm_obj.VoxelOrgan(label)

    for i in range(randrange(0, 10)):
        vo.voxel_segments.append(_generate_random_segment())

    return vo


def test_voxel_segmentation():

    voxels_size = 4

    vms = phm_obj.VoxelSegmentation(voxels_size)
    vms.voxel_organs.append(_generate_random_orange('leaf'))
    vms.voxel_organs.append(_generate_random_orange('leaf'))
    vms.voxel_organs.append(_generate_random_orange('leaf'))
    vms.voxel_organs.append(_generate_random_orange('stem'))

    # Write
    filename = 'tmp.json'
    vms.write_to_json_gz(filename)
    vms = phm_obj.VoxelSegmentation.read_from_json_gz(filename)
    os.remove(filename)

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
