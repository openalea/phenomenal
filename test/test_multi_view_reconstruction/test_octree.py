# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os

from alinea.phenomenal.data_structure import (
    VoxelOctree)
# ==============================================================================


def test_octree():

    world_coordinate = (0, 0, 0)
    voxel_size = 20
    data = True

    octree = VoxelOctree.from_position(world_coordinate, voxel_size, data)

    assert octree.root.position == world_coordinate
    assert octree.root.size == voxel_size
    assert octree.root.data == data
    assert octree.root.father is None
    assert octree.root.sons == [None, None, None, None, None, None, None, None]
    assert octree.root.is_leaf is True


def test_octree_1():
    world_coordinate = (0, 0, 0)
    voxel_size = 20
    data = True

    octree = VoxelOctree.from_position(world_coordinate, voxel_size, data)
    sons = octree.root.creates_sons()

    assert octree.root.is_leaf is False

    for son in sons:
        assert son is not None
        assert son.father is octree.root


def test_octree_2():
    world_coordinate = (0, 0, 0)
    voxel_size = 20
    data = True

    octree = VoxelOctree.from_position(world_coordinate, voxel_size, data)
    root = octree.root
    node = root.insert_node((10, 10, 10), True)


def test_octree_3():
    world_coordinate = (0, 0, 0)
    voxel_size = 20
    data = True

    octree = VoxelOctree.from_position(world_coordinate, voxel_size, data)
    octree.root.creates_sons()
    octree.root.sons[0].creates_sons()

    for node in octree.root.get_nodes():
        # print node
        continue


def test_octree_4():
    world_coordinate = (0, 0, 0)
    voxel_size = 20
    data = True

    octree = VoxelOctree.from_position(world_coordinate, voxel_size, data)
    octree.root.creates_sons()
    octree.root.sons[0].creates_sons()

    # print octree.root.get_leafs_formats_list()

    octree.write_to_json("test.json")
    octree = VoxelOctree.read_from_json("test.json")
    os.remove("test.json")

    print(octree.root)
    print(octree.root.sons[0])

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
