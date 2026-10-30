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
====
Mesh
====

.. currentmodule:: openalea.phenomenal.mesh

Algorithms
==========
.. autosummary::
   :toctree: generated/

   algorithms.meshing
   algorithms.marching_cubes
   algorithms.smoothing
   algorithms.decimation


Routines
========
.. autosummary::
   :toctree: generated/

   routines

"""

# ==============================================================================


from .algorithms import *
from .routines import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith("_")]
