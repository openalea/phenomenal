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
import json
import os
# ==============================================================================


class OcNode(object):
    def __init__(self, position, size, data, father):
        self.position = position
        self.size = size
        self.data = data

        self.father = father
        self.sons = [None, None, None, None, None, None, None, None]
        self.is_leaf = True

    def __str__(self):
        return """
        OcNode:
        \tposition : {0}
        \tsize : {1}
        \tdata: {2}
        \tis_leaf : {3}
        """.format(self.position, self.size, self.data, self.is_leaf)

    def creates_sons(self):
        r = self.size / 4.0

        x_min = self.position[0] - r
        x_max = self.position[0] + r

        y_min = self.position[1] - r
        y_max = self.position[1] + r

        z_min = self.position[2] - r
        z_max = self.position[2] + r

        self.sons = [
            OcNode((x_min, y_min, z_min), self.size / 2.0, self.data, self),
            OcNode((x_max, y_min, z_min), self.size / 2.0, self.data, self),
            OcNode((x_min, y_max, z_min), self.size / 2.0, self.data, self),
            OcNode((x_min, y_min, z_max), self.size / 2.0, self.data, self),
            OcNode((x_max, y_max, z_min), self.size / 2.0, self.data, self),
            OcNode((x_max, y_min, z_max), self.size / 2.0, self.data, self),
            OcNode((x_min, y_max, z_max), self.size / 2.0, self.data, self),
            OcNode((x_max, y_max, z_max), self.size / 2.0, self.data, self)]

        self.is_leaf = False

        return self.sons

    def get_nodes(self,
                  func_if_true_add_node=lambda n: True,
                  func_if_true_look_in_sons=lambda n: True,
                  func_get=lambda n: n):

        l = list()
        if func_if_true_add_node(self):
            l.append(func_get(self))

        if not self.is_leaf:
            if func_if_true_look_in_sons(self):
                for son in self.sons:
                    l.extend(son.get_nodes(
                        func_if_true_add_node=func_if_true_add_node,
                        func_if_true_look_in_sons=func_if_true_look_in_sons,
                        func_get=func_get))

        return l

    def get_leafs(self):

        def func_if_true_add_node(node):
            if node.is_leaf:
                return True
            else:
                return False

        return self.get_nodes(func_if_true_add_node=func_if_true_add_node)

    def in_it(self, position):

        r = self.size / 2.0

        x, y, z = position
        if self.position[0] - r <= x <= self.position[0] + r:
            if self.position[1] - r <= y <= self.position[1] + r:
                if self.position[2] - r <= z <= self.position[2] + r:
                    return True
        return False

    def get_neighbors_positions(self):

        cx, cy, cz = self.position

        cx_min, cx_max = cx - self.size, cx + self.size
        cy_min, cy_max = cy - self.size, cy + self.size
        cz_min, cz_max = cz - self.size, cz + self.size

        neighbors = [(cx, cy, cz_max),
                     (cx_min, cy, cz_max),
                     (cx_max, cy, cz_max),
                     (cx, cy_min, cz_max),
                     (cx_min, cy_min, cz_max),
                     (cx_max, cy_min, cz_max),
                     (cx, cy_max, cz_max),
                     (cx_min, cy_max, cz_max),
                     (cx_max, cy_max, cz_max),

                     (cx_min, cy, cz),
                     (cx_max, cy, cz),
                     (cx, cy_min, cz),
                     (cx_min, cy_min, cz),
                     (cx_max, cy_min, cz),
                     (cx, cy_max, cz),
                     (cx_min, cy_max, cz),
                     (cx_max, cy_max, cz),

                     (cx, cy, cz_min),
                     (cx_min, cy, cz_min),
                     (cx_max, cy, cz_min),
                     (cx, cy_min, cz_min),
                     (cx_min, cy_min, cz_min),
                     (cx_max, cy_min, cz_min),
                     (cx, cy_max, cz_min),
                     (cx_min, cy_max, cz_min),
                     (cx_max, cy_max, cz_min)]

        return neighbors

    def find_leaf_with_position(self, position):

        if self.in_it(position):
            if self.is_leaf:
                return self
            else:
                for son in self.sons:
                    leaf = son.find_leaf_with_position(position)
                    if leaf is not None:
                        return leaf
        else:
            return None

    def get_root(self):
        father = self.father
        if father is None:
            return self
        else:
            grandfather = father.father

            while grandfather is not None:
                father = grandfather
                grandfather = father.father

            return father

    def get_neighbors_leaf(self):

        neighbors_positions = self.get_neighbors_positions()

        root = self.get_root()

        neighbors_leaf = list()
        for position in neighbors_positions:

            leaf = root.find_leaf_with_position(position)

            if leaf is not None:
                neighbors_leaf.append(leaf)

        return neighbors_leaf

    def is_surrender(self):

        neighbors_positions = self.get_neighbors_positions()

        if self.father is None:
            return False
        else:
            for node in self.father.sons:
                if node is self:
                    continue

                if node.position in neighbors_positions:
                    if node.data is True:
                        neighbors_positions.remove(node.position)
                    else:
                        return False
                else:
                    return False

            root = self.get_root()
            for position in neighbors_positions:
                leaf = root.find_leaf_with_position(position)

                if leaf is None or leaf.data is False:
                    return False

            return True

    def depth(self):

        if self.is_leaf:
            return 0
        else:
            return 1 + max([node.depth() for node in self.sons])

    def insert_node(self, position, data):
        if self.in_it(position):

            if self.position == position:
                self.data = data
                return self

            if self.is_leaf:
                self.creates_sons()

            for son in self.sons:
                node = son.insert_node(position, data)

                if node is not None:
                    return node
        else:
            return None

    def get_dict_nodes(self):
        if self.is_leaf:

            return {"position": self.position,
                    "size": self.size,
                    "data": self.data,
                    "sons": None}
        else:

            sons = list()
            for leaf in self.sons:
                sons.append(leaf.get_dict_nodes())

            return {"position": self.position,
                    "size": self.size,
                    "data": self.data,
                    "sons": sons}


class Octree(object):

    def __init__(self):
        self.root = None

    @classmethod
    def from_oc_node(cls, node):
        octree = cls()
        octree.root = node
        return octree

    @classmethod
    def from_position(cls, position, size, data):
        octree = cls()
        octree.root = OcNode(position, size, data, None)
        return octree

    def get_leafs(self):

        if self.root is None:
            raise ValueError("No root define")

        return self.root.get_leafs()

    def get_nodes(self):

        if self.root is None:
            raise ValueError("No root define")

        return self.root.get_nodes()

    def get_leafs_with_data_equal_to(self, data):
        leafs = self.root.get_leafs()
        return [leaf for leaf in leafs if leaf.data == data]

    def get_nodes_with_size_equal_to(self, size):
        return self.root.get_nodes_with_size_equal_to(size)

    def get_nodes_with_size_and_data_equal_to(self, size, data):
        nodes = self.root.get_nodes_with_size_equal_to(size)
        return [node for node in nodes if node.data == data]

    def write_to_json(self, file_path):

        if self.root is None:
            raise ValueError("No root define")

        dict_nodes = self.root.get_dict_nodes()

        file_path = os.path.realpath(file_path)
        path_directory, file_name = os.path.split(file_path)

        if not os.path.exists(path_directory):
            os.makedirs(path_directory)

        with open(file_path, 'wb') as outfile:
            json.dump(dict_nodes, outfile)

    @staticmethod
    def create_oc_node(dict_node, father):

        position = dict_node["position"]
        data = dict_node["data"]
        size = dict_node["size"]
        dict_sons = dict_node["sons"]

        node = OcNode(position, size, data, father)

        if dict_sons is not None:
            node.is_leaf = False
            for i in range(len(dict_sons)):
                node.sons[i] = Octree.create_oc_node(dict_sons[i], node)
        else:
            node.is_leaf = True

        return node

    @staticmethod
    def read_from_json(file_path):

        with open(file_path, 'r') as infile:
            load_dict_octree = json.load(infile)

        root = Octree.create_oc_node(load_dict_octree, None)

        return Octree.from_oc_node(root)
