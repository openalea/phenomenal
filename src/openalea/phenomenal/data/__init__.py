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
=====================
Acces to plant's data
=====================

.. currentmodule:: openalea.phenomenal.data

.. autosummary::
   :toctree: generated/

   data

Synthetic data (for test)
=========================
.. autosummary::
   :toctree: generated/

    synthetic_data
"""

# ==============================================================================


from .synthetic_data import *
from .data import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith("_")]
