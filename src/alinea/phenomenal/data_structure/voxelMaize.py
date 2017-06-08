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
import json

from alinea.phenomenal.data_structure import VoxelOrgan
# ==============================================================================


class VoxelMaizeSegmentation(object):

    def __init__(self, voxels_size, ball_radius):
        self.voxel_organs = list()

        self.ball_radius = ball_radius
        self.voxels_size = voxels_size

    def get_leaf_order(self, number):
        for vs in self.voxel_segments:
            if "order" in vs.info and vs.info["order"] == number:
                return vs

    def swap_leaf_order(self, number_1, number_2):
        vs1 = self.get_leaf_order(number_1)
        vs2 = self.get_leaf_order(number_2)

        vs1.info['order'] = number_2
        vs2.info['order'] = number_1

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

    def get_cornet_leafs(self):
        cornet_leafs = list()
        for vo in self.voxel_organs:
            if vo.label == "cornet_leaf":
                cornet_leafs.append(vo)
        return cornet_leafs

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_json(self, filename):
        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'wb') as f:

            data = dict()
            data['ball_radius'] = self.ball_radius
            data['voxels_size'] = self.voxels_size

            data['voxel_organs'] = list()
            for vo in self.voxel_organs:

                dvo = dict()
                dvo['label'] = vo.label
                dvo['info'] = vo.info
                dvo['voxel_segments'] = list()

                for vs in vo.voxel_segments:
                    dvs = dict()
                    dvs['polyline'] = map(tuple, list(vs.polyline))
                    dvs['voxels_position'] = map(tuple,
                                                 list(vs.voxels_position))
                    dvo['voxel_segments'].append(dvs)

                data['voxel_organs'].append(dvo)

            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:
            data = json.load(f)

            vms = VoxelMaizeSegmentation(data['voxels_size'],
                                         data['ball_radius'])

            for dvo in data['voxel_organs']:

                vo = VoxelOrgan(dvo['label'])
                vo.info = dvo['info']

                for dvs in dvo['voxel_segments']:
                    voxels_position = set(map(tuple, dvs['voxels_position']))
                    polyline = map(tuple, list(dvs["polyline"]))

                    vo.add_voxel_segment(voxels_position, polyline)

                vms.voxel_organs.append(vo)

        return vms
