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

__name__ = 'Alinea.Phenomenal.algorithm.binarization'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.0.6'
__authors__ = 'C. Fournier'
__institutes__ = None
__icon__ = ''

__all__ = []


Phenomenal_algorithm_side_binarization_hsv = Factory(
    name='side_binarization_hsv',
    authors='Michael',
    description='',
    category='Binarization',
    nodemodule='alinea.phenomenal.binarization',
    nodeclass='side_binarization_hsv',

    inputs=[{'interface': None,
             'name': 'image'},
            {'interface': None,
             'name': 'configuration'}],

    outputs=[{'interface': None,
              'name': 'Binary image'}],
)
__all__.append('Phenomenal_algorithm_side_binarization_hsv')


Phenomenal_algorithm_side_binarization = Factory(
    name='side_binarization',
    authors='(C.Fournier)',
    description='',
    category='Binarization',
    nodemodule='alinea.phenomenal.binarization',
    nodeclass='side_binarization',

    inputs=[{'interface': None,
             'name': 'image'},
            {'interface': None,
             'name': 'mean_image'},
            {'interface': None,
             'name': 'configuration'}],

    outputs=[{'interface': None,
              'name': 'Binary image'}],
)
__all__.append('Phenomenal_algorithm_side_binarization')

Phenomenal_algorithm_side_binarization_elcom = Factory(
    name='side_binarization_elcom',
    authors='Elcom',
    description='',
    category='Binarization',
    nodemodule='alinea.phenomenal.binarization',
    nodeclass='side_binarization_elcom',

    inputs=[{'interface': None,
             'name': 'image'},
            {'interface': None,
             'name': 'mean_image'},
            {'interface': None,
             'name': 'configuration'}],

    outputs=[{'interface': None,
              'name': 'Binary image'}],
)
__all__.append('Phenomenal_algorithm_side_binarization_elcom')

Phenomenal_algorithm_side_binarization_adaptive_thresh = Factory(
    name='side_binarization_adaptive_thresh',
    authors='Simon',
    description='',
    category='Binarization',
    nodemodule='alinea.phenomenal.binarization',
    nodeclass='side_binarization_adaptive_thresh',

    inputs=[{'interface': None,
             'name': 'image'},
            {'interface': None,
             'name': 'configuration'}],

    outputs=[{'interface': None,
              'name': 'Binary image'}],
)
__all__.append('Phenomenal_algorithm_side_binarization_adaptive_thresh')
