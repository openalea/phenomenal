# -*- python -*-
#
#       __wralea__.py: Module Description
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

__revision__ = ""

#       =======================================================================
#       Local Import
from openalea.core import *

#       =======================================================================
#       Code

__name__ = 'Alinea.Phenomenal.tools'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.0.6'
__authors__ = 'S. Artzet'
__institutes__ = None
__icon__ = ''

__all__ = []


Phenomenal_tools_get_time = Factory(
    name='get_time',
    authors='Simon Artzet',
    description='',
    category='tools',
    nodemodule='alinea.phenomenal.tools',
    nodeclass='get_time',

    inputs=[{'interface': None,
              'name': 'argument'}],

    outputs=[{'interface': None,
              'name': 'argument'},
             {'interface': None,
              'name': 'Current time'}],
)
__all__.append('Phenomenal_tools_get_time')
