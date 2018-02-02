
# This file has been generated at Wed Jan 17 18:30:12 2018

from openalea.core import *


__name__ = 'openalea.phenomenal_wralea.phenoarch'

__editable__ = True
__version__ = '1.6.0'
__license__ = 'CeCILL-C'
__authors__ = 'Me'


__all__ = ['openalea_phenomenal_phenoarch_routine_side_binarization',
           'openalea_phenomenal_phenoarch_routine_top_binarization',
           'openalea_phenomenal_phenoarch_binarize',
           'openalea_phenomenal_phenoarch_get_image_views',
           'openalea_phenomenal_phenoarch_show_voxel_grid']



openalea_phenomenal_phenoarch_routine_side_binarization = Factory(
                name='routine_side_binarization',
                authors='Me (wralea authors)',
                description='',
                category='openalea.phenomenal_wralea.phenoarch',
                nodemodule='openalea.phenomenal_wralea.phenoarch.binarization',
                nodeclass='routine_side_binarization',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )

openalea_phenomenal_phenoarch_routine_top_binarization = Factory(
                name='routine_top_binarization',
                authors='Me (wralea authors)',
                description='',
                category='openalea.phenomenal_wralea.phenoarch',
                nodemodule='openalea.phenomenal_wralea.phenoarch.binarization',
                nodeclass='routine_top_binarization',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )

openalea_phenomenal_phenoarch_binarize = Factory(
                name='binarize',
                authors='Me (wralea authors)',
                description='',
                category='openalea.phenomenal_wralea.phenoarch',
                nodemodule='openalea.phenomenal_wralea.phenoarch.binarization',
                nodeclass='binarize',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )

openalea_phenomenal_phenoarch_get_image_views = Factory(
                name='get_image_views',
                authors='Me (wralea authors)',
                description='',
                category='openalea.phenomenal_wralea.phenoarch',
                nodemodule='openalea.phenomenal_wralea.phenoarch.reconstruction_3d',
                nodeclass='get_image_views',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )


openalea_phenomenal_phenoarch_show_voxel_grid = Factory(
                name='show_voxel_grid',
                authors='Me (wralea authors)',
                description='',
                category='openalea.phenomenal_wralea.phenoarch',
                nodemodule='openalea.phenomenal_wralea.phenoarch.display',
                nodeclass='show_voxel_grid',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
               )

