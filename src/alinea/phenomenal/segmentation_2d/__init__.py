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
"""
===============
Segmentation 2D
===============

.. currentmodule:: alinea.phenomenal.segmentation_2d

Skeletonize
===========

.. automodule:: alinea.phenomenal.segmentation_2d.skeletonize
.. currentmodule:: alinea.phenomenal.segmentation_2d

.. autosummary::
   :toctree: generated/

    skeletonize
    skeletonize_thinning
    skeletonize_erode_dilate

"""
# ==============================================================================

from alinea.phenomenal.segmentation_2d.segmentation_2d import (
    Segment, Organ, Stem, Leaf)

from alinea.phenomenal.segmentation_2d.skeletonize import (
    skeletonize,
    skeletonize_thinning,
    skeletonize_erode_dilate)
