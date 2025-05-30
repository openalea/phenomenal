# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import os
import gzip
import json

from .voxelOrgan import VoxelOrgan
# ==============================================================================


class VoxelSegmentation:
    def __init__(self, voxels_size):
        self.voxel_organs = []
        self.voxels_size = voxels_size
        self.info = {}

    def update_plant_info(self):
        s = set()
        for vo in self.voxel_organs:
            s = s.union(vo.voxels_position())

        self.info["pm_label"] = "plant"
        self.info["pm_voxels_volume"] = len(s) * self.voxels_size**3
        self.info["pm_number_of_leaf"] = self.get_number_of_leaf()

    def get_voxels_position(self, except_organs=None):
        if except_organs is None:
            except_organs = []

        voxels_position = set()
        for vo in self.voxel_organs:
            if vo not in except_organs:
                voxels_position = voxels_position.union(vo.voxels_position())

        return voxels_position

    def get_number_of_leaf(self):
        number = 0
        for vo in self.voxel_organs:
            if vo.label in ("growing_leaf", "mature_leaf"):
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

        vs1.info["pm_leaf_number"] = number_2
        vs2.info["pm_leaf_number"] = number_1

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
        mature_leafs = []
        for vo in self.voxel_organs:
            if vo.label == "mature_leaf":
                mature_leafs.append(vo)
        return mature_leafs

    def get_growing_leafs(self):
        growing_leafs = []
        for vo in self.voxel_organs:
            if vo.label == "growing_leaf":
                growing_leafs.append(vo)
        return growing_leafs

    def get_leafs(self):
        leafs = []
        for vo in self.voxel_organs:
            if vo.label in ("growing_leaf", "mature_leaf"):
                leafs.append(vo)
        return leafs

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_json_gz(self, filename):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with gzip.open(filename, "wb") as f:
            data = {
                "voxels_size": self.voxels_size,
                "voxel_organs": [],
                "info": self.info,
            }

            for vo in self.voxel_organs:
                dvo = {
                    "label": vo.label,
                    "sub_label": vo.sub_label,
                    "info": vo.info,
                    "voxel_segments": [],
                }

                for vs in vo.voxel_segments:
                    dvs = {
                        "polyline": list(map(tuple, list(vs.polyline))),
                        "voxels_position": list(map(tuple, list(vs.voxels_position))),
                    }
                    dvo["voxel_segments"].append(dvs)

                data["voxel_organs"].append(dvo)

            f.write(json.dumps(data).encode("utf-8"))

    @staticmethod
    def read_from_json_gz(filename, without_info=False):
        with gzip.open(filename, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
            # data = ast.literal_eval(f.read())

            vms = VoxelSegmentation(data["voxels_size"])

            for dvo in data["voxel_organs"]:
                vo = VoxelOrgan(dvo["label"])

                if "sub_label" in dvo:
                    vo.sub_label = dvo["sub_label"]

                if not without_info:
                    vo.info = dvo["info"]

                for dvs in dvo["voxel_segments"]:
                    voxels_position = set(map(tuple, dvs["voxels_position"]))
                    polyline = list(map(tuple, list(dvs["polyline"])))

                    vo.add_voxel_segment(voxels_position, polyline)

                vms.voxel_organs.append(vo)

            vms.update_plant_info()

        return vms
