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
import sys
import gzip
import orjson
import numpy

from .voxelGrid import VoxelGrid
from .voxelSegment import VoxelSegment
# ==============================================================================


class VoxelSkeleton:
    def __init__(self, segments, voxels_size):
        self.segments = segments
        self.voxels_size = voxels_size

    def voxels_position(self):
        voxels_position = set()
        for segment in self.segments:
            voxels_position = voxels_position.union(segment.voxels_position)
        return numpy.array(list(voxels_position))

    def voxels_position_polyline(self):
        voxels_position = set()
        for segment in self.segments:
            voxels_position = voxels_position.union(segment.polyline)
        return numpy.array(list(voxels_position))

    def volume(self):
        return len(self.voxels_position()) * self.voxels_size**3

    def to_voxel_grid(self):
        return VoxelGrid(self.voxels_position(), self.voxels_size)

    def write_to_json_gz(self, filename):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with gzip.open(filename, "wb") as f:
            data = {"segments": [], "voxels_size": self.voxels_size}

            for seg in self.segments:
                dseg = {
                    "voxels_position": list(seg.voxels_position),
                    "polyline": seg.polyline,
                    "closest_nodes": [list(nodes) for nodes in seg.closest_nodes],
                }
                data["segments"].append(dseg)

            f.write(orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY))

    @staticmethod
    def read_from_json_gz(filename):
        with gzip.open(filename, "rb") as f:
            try:
                data = orjson.loads(f.read().decode("utf-8"))
            except:
                print(f"Cannot open file {filename}", file=sys.stderr)
                return None
            segs = []

            for dseg in data["segments"]:
                polyline = list(map(tuple, dseg["polyline"]))
                voxels_position = set(list(map(tuple, dseg["voxels_position"])))
                closest_nodes = [
                    set(list(map(tuple, nodes))) for nodes in dseg["closest_nodes"]
                ]
                segs.append(VoxelSegment(polyline, voxels_position, closest_nodes))

            sk = VoxelSkeleton(segs, data["voxels_size"])

        return sk
