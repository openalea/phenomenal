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
Segmentation 3D
===============

.. currentmodule:: openalea.phenomenal.3D_segmentation


Segmentation
============

.. automodule:: openalea.phenomenal.3D_segmentation.segmentation
.. currentmodule:: openalea.phenomenal.3D_segmentation

.. autosummary::
   :toctree: generated/

    maize_segmentation

Graph
=====

.. automodule:: openalea.phenomenal.3D_segmentation.graph
.. currentmodule:: openalea.phenomenal.3D_segmentation

.. autosummary::
   :toctree: generated/

    create_graph
    add_nodes

Peak Detect
===========
.. automodule:: openalea.phenomenal.3D_segmentation.peakdetect
.. currentmodule:: openalea.phenomenal.3D_segmentation

.. autosummary::
   :toctree: generated/

    peakdetect


Thinning
========

.. automodule:: openalea.phenomenal.3D_segmentation.thinning
.. currentmodule:: openalea.phenomenal.3D_segmentation

.. autosummary::
   :toctree: generated/

    thinning_3d
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import


from .graph import *
from .thinning import *
from .algorithm import *
from .skeleton import *
from .graph import *
# from .skeleton_accurate import *
from .plant_analysis import *
from .maize import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
