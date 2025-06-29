# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


# ==============================================================================


class ImageView:
    def __init__(self, image, projection, inclusive=False, image_ref=None):
        self.image = image
        self.projection = projection
        self.inclusive = inclusive
        self.image_ref = image_ref
