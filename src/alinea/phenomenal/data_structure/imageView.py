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

# ==============================================================================


class ImageView(object):

    def __init__(self, image, projection, inclusive=False, ref=False):
        self.image = image
        self.projection = projection
        self.inclusive = inclusive
        self.ref = ref

