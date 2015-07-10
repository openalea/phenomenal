
# This file has been generated at Fri Oct 25 15:59:42 2013

from openalea.core import *


__name__ = 'Alinea.Phenomenal.configuration'

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

configlist=['SideCamera2013_ZoomOut.cfg']

Phenomenal_configreader = Factory(name='configreader',
                               authors='(C. Fournier)',
                               description='Loads configfile for binarization',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'getconfig',
                               inputs=[{'interface': IFileStr, 'name': 'ConfigFile', 'desc': 'Configurationfile to be loaded.'}],
                               outputs=({'interface': None, 'name': 'out', 'desc': 'p config dict.'},),
                               )

__all__.append('Phenomenal_configreader')

Phenomenal_loadconfig = Factory(name='load config',
                               authors='(C. Fournier)',
                               description='Loads configfile for binarization',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'loadconfig',
                               inputs=[{'interface':IEnumStr(enum=configlist), 'name': 'configuration', 'value': 'SideCamera2013_ZoomOut.cfg'}],
                               outputs=({'interface': None, 'name': 'out', 'desc': 'p config dict.'},),
                               )

__all__.append('Phenomenal_loadconfig')

Phenomenal_sidebinconfiguration = Factory(name='sidebin_configuration',
                               authors='(C. Fournier)',
                               description='Parses configfile for side binarization',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'sidebinarisation_configuration',
                               inputs=[{'interface': None, 'name': 'configuration', 'desc': 'phenomenal config parser'}],
                               outputs=[{'interface': IDict, 'name': 'crop domain', 'desc': ''},
                                        {'interface': None, 'name': 'main_optimizer options', 'desc': ''},
                                        {'interface': None, 'name': 'band_optimizer options', 'desc': ''},
                                        {'interface': None, 'name': 'pot_optimizer options', 'desc': ''},],
                               )
__all__.append('Phenomenal_sidebinconfiguration')

Phenomenal_topbinconfiguration = Factory(name='topbin_configuration',
                               authors='(C. Fournier)',
                               description='Parses configfile for side binarization',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'topbinarisation_configuration',
                               inputs=[{'interface': None, 'name': 'configuration', 'desc': 'phenomenal config parser'}],
                               outputs=[{'interface': None, 'name': 'main_optimizer options', 'desc': ''},],
                               )
__all__.append('Phenomenal_topbinconfiguration')

Phenomenal_cropdomain = Factory(name='crop domain',
                               authors='(C. Fournier)',
                               description='expand crop domain dict',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'crop_domain_node',
                               inputs=[{'interface': None, 'name': 'domain', 'desc': ''}],
                               outputs=[{  'desc': '', 'interface': IInt, 'name': 'y1', 'value': None},
                                        {  'desc': '', 'interface': IInt, 'name': 'y2', 'value': None},
                                        {  'desc': '', 'interface': IInt, 'name': 'x1', 'value': None},
                                        {  'desc': '', 'interface': IInt, 'name': 'x2', 'value': None},],
                               )
__all__.append('Phenomenal_cropdomain')

Phenomenal_importimages = Factory(name='import_images',
                               authors='(C. Fournier)',
                               description='get image paths',
                               category='Data I/O',
                               nodemodule = 'alinea.phenomenal.configuration',
                               nodeclass = 'import_images',
                               inputs=[{'interface': IDirStr, 'name': 'Data dir', 'desc': 'Directory containing plant folders'},
                               {'interface': IStr, 'name': 'Genotype', 'desc': 'name of sub-directory containing plant images'},
                               {'interface': IStr, 'name': 'Plant_id', 'desc': 'plant identifier'}],
                               outputs=({'interface': IDict, 'name': 'images', 'desc': ''},),
                               )
__all__.append('Phenomenal_importimages')


Phenomenal_binarization_config = Factory(
    name='binarization_config',
    authors='(S. Artzet)',
    description='',
    category='Data I/O',
    nodemodule='alinea.phenomenal.configuration',
    nodeclass='binarization_config',
    inputs=[
        {'interface': None,
         'name': 'config',
         'desc': 'config from load_config function'}],
    outputs=({'interface': None,
              'name': 'out',
              'desc': 'Object BinarizationConfig'},),
)
__all__.append('Phenomenal_binarization_config')

Phenomenal_read_config = Factory(
    name='read_config',
    authors='(S. Artzet)',
    description='',
    category='Data I/O',
    nodemodule='alinea.phenomenal.configuration',
    nodeclass='read_config',
    inputs=[
        {'interface': IFileStr,
         'name': 'config_file'}],
    outputs=({'interface': None,
              'name': 'out'},),
)
__all__.append('Phenomenal_read_config')

Phenomenal_config_value = Factory(
    name='config_value',
    authors='(S. Artzet)',
    description='Return value from the dictionary config loaded',
    category='Data I/O',
    nodemodule='alinea.phenomenal.configuration',
    nodeclass='config_value',
    inputs=[
        {'interface': None,
         'name': 'config',
         'desc': 'config from load_config function'}],
    outputs=({'interface': None, 'name': 'out', 'desc': ''},),
)
__all__.append('Phenomenal_config_value')
