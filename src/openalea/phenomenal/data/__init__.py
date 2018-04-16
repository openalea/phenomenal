# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
Data sub packge to manage data exemple and test for phenomenal package
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

from .synthetic_data import *
from .data import *
# ==============================================================================

__all__ = [s for s in dir() if not s.startswith('_')]
