# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
=========================
Multi-View Reconstruction
=========================

.. currentmodule:: openalea.phenomenal.multi_view_reconstruction

Main's function
===============
.. autosummary::
   :toctree: generated/

    multi_view_reconstruction
    _multi_view_reconstruction_octree

"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .multi_view_reconstruction import *
from ._multi_view_reconstruction_octree import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
