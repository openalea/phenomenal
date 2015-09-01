# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import

#       =======================================================================
#       Local Import 

#       =======================================================================
#       Code


class OctNode:
    # New Octnode Class, can be appended to as well i think
    def __init__(self, position, size):
        # OctNode Cubes have a position and size
        # position is related to, but not the same as the objects the node contains.
        self.position = position
        self.size = size

        # All OctNodes will be leaf nodes at first
        # Then subdivided later as more objects get added
        self.isLeafNode = True

        # store our object, typically this will be one, but maybe more
        self.data = None

        # might as well give it some emtpy branches while we are here.
        self.branches = [None, None, None, None, None, None, None, None]
        self.parent = None

        # The cube's bounding coordinates -- Not currently used
        self.ldb = (position[0] - (size / 2), position[1] - (size / 2), position[2] - (size / 2))
        self.ruf = (position[0] + (size / 2), position[1] + (size / 2), position[2] + (size / 2))

    def create_children(self):
        self.branches[0] = OctNode(self.position, self.size / 2, self)
        self.branches[1] = OctNode(self.position, self.size / 2, self)
        self.branches[2] = OctNode(self.position, self.size / 2, self)
        self.branches[3] = OctNode(self.position, self.size / 2, self)
        self.branches[4] = OctNode(self.position, self.size / 2, self)
        self.branches[5] = OctNode(self.position, self.size / 2, self)
        self.branches[6] = OctNode(self.position, self.size / 2, self)
        self.branches[7] = OctNode(self.position, self.size / 2, self)


#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None