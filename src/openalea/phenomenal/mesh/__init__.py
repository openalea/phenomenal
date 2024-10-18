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

Formats
=======
.. autosummary::
   :toctree: generated/

   formats


Routines
========
.. autosummary::
   :toctree: generated/

   routines


VTK Transformation
==================
.. autosummary::
   :toctree: generated/

   vtk_transformation

"""

# ==============================================================================
from __future__ import division, print_function, absolute_import

from .algorithms import *
from .formats import *
from .routines import *
from .vtk_transformation import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith("_")]
