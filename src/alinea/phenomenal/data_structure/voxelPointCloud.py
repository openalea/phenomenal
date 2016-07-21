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
import collections
# ==============================================================================


class VoxelPointCloud(object):

    def __init__(self,
                 voxel_centers=collections.deque(),
                 voxel_size=1):

        self.voxel_centers = voxel_centers
        self.voxel_size = voxel_size

    def bounding_box(self):

        if not self.voxel_centers:
            raise ValueError("Empty list")

        x_min = float("inf")
        y_min = float("inf")
        z_min = float("inf")

        x_max = - float("inf")
        y_max = - float("inf")
        z_max = - float("inf")

        for x, y, z in self.voxel_centers:
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

        Returns
        -------
        out : int
            Error value
        """

        return len(self.voxel_centers) * self.voxel_size ** 3
