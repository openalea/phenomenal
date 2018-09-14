# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import ast
import os
import gzip

from .voxelOrgan import VoxelOrgan
# ==============================================================================


class VoxelSegmentation(object):

    def __init__(self, voxels_size):

        self.voxel_organs = list()
        self.voxels_size = voxels_size
        self.info = dict()

    def update_plant_info(self):
        s = set()
        for vo in self.voxel_organs:
            s = s.union(vo.voxels_position())

        self.info["pm_label"] = 'plant'
        self.info["pm_voxels_volume"] = len(s) * self.voxels_size ** 3
        self.info["pm_number_of_leaf"] = self.get_number_of_leaf()


    def get_voxels_position(self, except_organs=None):

        if except_organs is None:
            except_organs = list()

        voxels_position = set()
        for vo in self.voxel_organs:
            if vo not in except_organs:
                voxels_position = voxels_position.union(vo.voxels_position())

        return voxels_position

    def get_number_of_leaf(self):
        number = 0
        for vo in self.voxel_organs:
            if vo.label == "mature_leaf" or vo.label == "growing_leaf":
                number += 1

        return number

    def get_leaf_order(self, number):
        for vo in self.voxel_organs:
            if "pm_leaf_number" in vo.info and vo.info["pm_leaf_number"] == number:
                return vo
        return None

    def swap_leaf_order(self, number_1, number_2):
        vs1 = self.get_leaf_order(number_1)
        vs2 = self.get_leaf_order(number_2)

        vs1.info['pm_leaf_number'] = number_2
        vs2.info['pm_leaf_number'] = number_1

    def get_stem(self):
        for vo in self.voxel_organs:
            if vo.label == "stem":
                return vo
        return None

    def get_unknown(self):
        for vo in self.voxel_organs:
            if vo.label == "unknown":
                return vo
        return None

    def get_mature_leafs(self):
        mature_leafs = list()
        for vo in self.voxel_organs:
            if vo.label == "mature_leaf":
                mature_leafs.append(vo)
        return mature_leafs

    def get_growing_leafs(self):
        growing_leafs = list()
        for vo in self.voxel_organs:
            if vo.label == "growing_leaf":
                growing_leafs.append(vo)
        return growing_leafs

    def get_leafs(self):

        leafs = list()
        for vo in self.voxel_organs:
            if vo.label == "growing_leaf" or vo.label == "mature_leaf":
                leafs.append(vo)
        return leafs

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_json_gz(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with gzip.open(filename, 'wb') as f:

            data = dict()
            data['voxels_size'] = self.voxels_size
            data['voxel_organs'] = list()
            data['info'] = self.info

            for vo in self.voxel_organs:

                dvo = dict()
                dvo['label'] = vo.label
                dvo['sub_label'] = vo.sub_label
                dvo['info'] = vo.info
                dvo['voxel_segments'] = list()

                for vs in vo.voxel_segments:
                    dvs = dict()
                    dvs['polyline'] = map(tuple, list(vs.polyline))
                    dvs['voxels_position'] = map(
                        tuple, list(vs.voxels_position))
                    dvo['voxel_segments'].append(dvs)

                data['voxel_organs'].append(dvo)

            f.write(str(data))

    @staticmethod
    def read_from_json_gz(filename, without_info=False):

        with gzip.open(filename, 'rb') as f:
            data = ast.literal_eval(f.read())

            vms = VoxelSegmentation(data['voxels_size'])

            for dvo in data['voxel_organs']:

                vo = VoxelOrgan(dvo['label'])

                if 'sub_label' in dvo:
                    vo.sub_label = dvo['sub_label']

                if not without_info:
                    vo.info = dvo['info']

                for dvs in dvo['voxel_segments']:
                    voxels_position = set(map(tuple, dvs['voxels_position']))
                    polyline = map(tuple, list(dvs["polyline"]))

                    vo.add_voxel_segment(voxels_position, polyline)

                vms.voxel_organs.append(vo)

            vms.update_plant_info()

        return vms
