# This file has been generated at Fri Jun 19 16:26:19 2015

from openalea.core import *

__name__ = 'Alinea.Phenomenal'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.0.6'
__authors__ = 'M.Mielewczik, C.Fournier'
__institutes__ = None
__icon__ = ''

__all__ = ['alinea_phenomenal_Phenomenal_db_createSSHClient',
           'alinea_phenomenal_Phenomenal_export_csvoutputall',
           'alinea_phenomenal_Phenomenal_db_scpconnect']

alinea_phenomenal_Phenomenal_db_createSSHClient = Factory(
    name='createSSHClient',
    authors='(M.Mielewczik)',
    description='',
    category='Unclassified',
    nodemodule='alinea.phenomenal.Phenomenal_db',
    nodeclass='createSSHClient',
    inputs=None,
    outputs=({'interface': None, 'name': 'out'},),
    widgetmodule=None,
    widgetclass=None,
)



alinea_phenomenal_Phenomenal_db_scpconnect = Factory(
    name='scpconnect',
    authors=' (M.Mielewczik)',
    description='',
    category='Unclassified',
    nodemodule='alinea.phenomenal.Phenomenal_db',
    nodeclass='scpconnect',
    inputs=None,
    outputs=(
        {'interface': None,
         'name': 'out'},),
    widgetmodule=None,
    widgetclass=None,
)
