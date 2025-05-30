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
import re
import json
import csv
import numpy

from .image3D import Image3D


# ==============================================================================


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, o):
        if isinstance(o, numpy.integer):
            return int(o)
        if isinstance(o, numpy.floating):
            return float(o)
        if isinstance(o, numpy.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)


class VoxelGrid:
    def __init__(self, voxels_position, voxels_size):
        self._voxels_position = voxels_position
        self._voxels_size = voxels_size

    # ==========================================================================
    # GETTER & SETTER
    # ==========================================================================

    @property
    def voxels_position(self):
        return self._voxels_position

    @voxels_position.setter
    def voxels_position(self, voxels_position):
        self._voxels_position = voxels_position

    @voxels_position.deleter
    def voxels_position(self):
        del self._voxels_position

    @property
    def voxels_size(self):
        return self._voxels_size

    @voxels_size.setter
    def voxels_size(self, voxels_size):
        self._voxels_size = voxels_size

    @voxels_size.deleter
    def voxels_size(self):
        del self._voxels_size

    # ==========================================================================
    # Analysis Data
    # ==========================================================================

    def bounding_box(self):
        if len(self._voxels_position) == 0:
            raise ValueError("Empty list")

        x_min = float("inf")
        y_min = float("inf")
        z_min = float("inf")

        x_max = -float("inf")
        y_max = -float("inf")
        z_max = -float("inf")

        for x, y, z in self._voxels_position:
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            z_min = min(z_min, z)

            x_max = max(x_max, x)
            y_max = max(y_max, y)
            z_max = max(z_max, z)

        return (x_min, y_min, z_min), (x_max, y_max, z_max)

    def volume(self):
        """
        Compute the volume of the voxel point cloud
        """

        return len(self._voxels_position) * self._voxels_size**3

    def __len__(self):
        return len(self._voxels_position)

    # ==========================================================================
    # SHOW
    # ==========================================================================

    def show(self):
        raise NotImplementedError

    # ==========================================================================
    # TRANSFORM
    # ==========================================================================

    def to_image_3d(self):
        (x_min, y_min, z_min), (x_max, y_max, z_max) = self.bounding_box()

        len_x = int((x_max - x_min) / self.voxels_size + 1)
        len_y = int((y_max - y_min) / self.voxels_size + 1)
        len_z = int((z_max - z_min) / self.voxels_size + 1)

        image_3d = Image3D.zeros(
            (len_x, len_y, len_z),
            dtype=bool,
            voxels_size=self.voxels_size,
            world_coordinate=(x_min, y_min, z_min),
        )

        bound_min = numpy.array((x_min, y_min, z_min))
        vs_pos = numpy.array(self.voxels_position)

        r = ((vs_pos - bound_min) / self.voxels_size).astype(int)
        image_3d[r[:, 0], r[:, 1], r[:, 2]] = 1

        return image_3d

    @staticmethod
    def from_image_3d(
        image_3d, voxels_value=1, voxels_size=None, world_coordinate=None
    ):
        xx, yy, zz = numpy.where(image_3d >= voxels_value)

        if voxels_size is None:
            voxels_size = image_3d.voxels_size

        if world_coordinate is None:
            world_coordinate = image_3d.world_coordinate

        xxx = world_coordinate[0] + xx * voxels_size
        yyy = world_coordinate[1] + yy * voxels_size
        zzz = world_coordinate[2] + zz * voxels_size

        voxels_position = numpy.column_stack((xxx, yyy, zzz))

        return VoxelGrid(voxels_position, voxels_size)

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write(self, filename):
        ext = filename.split(".")[-1]

        if ext == "npz":
            return self.write_to_npz(filename)
        if ext == "json":
            return self.write_to_json(filename)
        if ext == "csv":
            return self.write_to_csv(filename)
        if ext == "xyz":
            return self.write_to_xyz(filename)

        raise ValueError("No extension")

    @staticmethod
    def read(filename, voxel_size=None):
        ext = filename.split(".")[-1]

        if ext == "npz":
            return VoxelGrid.read_from_npz(filename)
        if ext == "json":
            return VoxelGrid.read_from_json(filename)
        if ext == "csv":
            return VoxelGrid.read_from_csv(filename)
        if ext == "xyz":
            return VoxelGrid.read_from_xyz(filename, voxel_size)

        raise ValueError("No extension")

    def write_to_npz(self, filename):
        image_3d = self.to_image_3d()
        image_3d.write_to_npz(filename)

    @staticmethod
    def read_from_npz(filename):
        image_3d = Image3D.read_from_npz(filename)
        return VoxelGrid.from_image_3d(image_3d)

    def write_to_json(self, filename):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, "w", encoding="UTF8") as f:
            data = {"voxels_size": self.voxels_size}
            vp = list(map(tuple, self.voxels_position))
            data["voxels_position"] = json.dumps(vp, cls=NumpyEncoder)
            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):
        with open(filename, "r", encoding="UTF8") as f:
            data = json.load(f)
            voxels_size = data["voxels_size"]
            voxels_position = json.loads(data["voxels_position"])

            return VoxelGrid(voxels_position, voxels_size)

    def write_to_xyz(self, filename):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, "w", encoding="UTF8") as f:
            for x, y, z in self.voxels_position:
                f.write(f"{x} {y} {z} \n")

    @staticmethod
    def read_from_xyz(filename, voxels_size):
        voxels_position = []
        with open(filename, "r", encoding="UTF8") as f:
            for line in f:
                values = [float(v) for v in line.split()[:3]]
                voxels_position.append(tuple(values))
        f.close()

        return VoxelGrid(voxels_position, voxels_size)

    def write_to_csv(self, filename, header=None):
        if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        if header is None:
            header = {}
        header.update({"voxels_size": self.voxels_size})

        with open(filename, "w", newline="", encoding="UTF8") as f:
            c = csv.writer(f)
            for k, v in header.items():
                c.writerow(["# " + k + ": " + str(v)])
            c.writerow(["x_coord", "y_coord", "z_coord"])

            for x, y, z in self.voxels_position:
                c.writerow([x, y, z])

    @staticmethod
    def read_from_csv(filename, read_header=False):
        voxels_position = []
        header = {}

        with open(filename, "r", newline="", encoding="UTF8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0].split("#")[0].strip():
                    break
                k, v = row[0].split("#")[1].strip().split(":")
                header[k.strip()] = v.strip()

            if "voxels_size" in header:
                voxels_size = float(header["voxels_size"])
                for x, y, z in reader:
                    voxels_position.append((float(x), float(y), float(z)))
            else:
                x, y, z, vs = next(reader)
                voxels_size = float(vs)
                voxels_position.append((float(x), float(y), float(z)))
                for x, y, z, _ in reader:
                    voxels_position.append((float(x), float(y), float(z)))
            if read_header:
                return VoxelGrid(voxels_position, voxels_size), header
            return VoxelGrid(voxels_position, voxels_size)
