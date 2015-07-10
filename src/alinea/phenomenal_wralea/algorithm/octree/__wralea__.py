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

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 


#       =======================================================================
#       Local Import 


#       =======================================================================
#       Code
#       =======================================================================
#       Local Import
from openalea.core import *

#       =======================================================================
#       Code

__name__ = 'Alinea.Phenomenal.algorithm.octree'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.0.6'
__authors__ = ''
__institutes__ = None
__icon__ = ''

__all__ = []


Phenomenal_algorithm_octree = Factory(
    name='octree',
    authors='',
    description='',
    category='3D_RECONSTRUCTION',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='octree',

    inputs=[{'interface': None,
             'name': 'image'},
            {'interface': None,
             'name': 'angle'},
            {'interface': None,
             'name': 'calibration'},
            {'interface': None,
             'name': 'precision',
             'value': 1},
            {'interface': None,
             'name': 'use_top_image',
             'value': True}],

    outputs=[{'interface': None,
              'name': '3D octree'}],
)
__all__.append('Phenomenal_algorithm_octree')


Phenomenal_algorithm_load_images = Factory(
    name='load_images',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='load_images',

    inputs=[{'interface': None,
             'name': 'paths_files'}],

    outputs=[{'interface': None,
              'name': 'images'}],
)
__all__.append('Phenomenal_algorithm_load_images')


Phenomenal_algorithm_binarize_images = Factory(
    name='binarize_images',
    authors='',
    description='',
    category='3D_RECONSTRUCTION',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='binarize_images',

    inputs=[{'interface': None,
             'name': 'images'}],

    outputs=[{'interface': None,
              'name': 'Binarize images'}],
)
__all__.append('Phenomenal_algorithm_binarize_images')

Phenomenal_algorithm_get_configuration_camera = Factory(
    name='get_configuration_camera',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='get_configuration_camera',

    inputs=[],

    outputs=[{'interface': None,
              'name': 'configuration_camera'}],
)
__all__.append('Phenomenal_algorithm_get_configuration_camera')


Phenomenal_algorithm_get_calibration = Factory(
    name='get_calibration',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='get_calibration',

    inputs=[{'interface': None,
             'name': 'configuration_camera'}],

    outputs=[{'interface': None,
              'name': 'calibration'}],
)
__all__.append('Phenomenal_algorithm_get_calibration')


Phenomenal_algorithm_create_matrix = Factory(
    name='create_matrix',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='create_matrix',

    inputs=[{'interface': None,
             'name': 'calibration'}],

    outputs=[{'interface': None,
              'name': 'matrix'}],
)
__all__.append('Phenomenal_algorithm_create_matrix')


Phenomenal_algorithm_fill_matrix = Factory(
    name='fill_matrix',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='fill_matrix',

    inputs=[{'interface': None,
             'name': 'cubes'},
            {'interface': None,
             'name': 'matrix'}],

    outputs=[{'interface': None,
              'name': 'matrix'}],
)
__all__.append('Phenomenal_algorithm_fill_matrix')

Phenomenal_algorithm_write_images_on_matrix = Factory(
    name='write_images_on_matrix',
    authors='',
    description='',
    category='',
    nodemodule='alinea.phenomenal.octree',
    nodeclass='write_images_on_matrix',

    inputs=[{'interface': None,
             'name': 'images'},
            {'interface': None,
             'name': 'matrix'}],

    outputs=[{'interface': None,
              'name': 'matrix'}],
)
__all__.append('Phenomenal_algorithm_write_images_on_matrix')
