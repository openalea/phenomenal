# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .displayVoxel import DisplayVoxel
# ==============================================================================


class DisplayMesh(DisplayVoxel):

    def __init__(self):
        DisplayVoxel.__init__(self)

    def __call__(self, vertices, faces, color=(0, 0.8, 0)):
        self.add_actor_from_vertices_faces(vertices, faces, color=color)
        self.show()