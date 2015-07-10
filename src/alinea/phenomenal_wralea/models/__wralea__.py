
# This file has been generated at Fri Oct 25 15:59:42 2013

from openalea.core import *


__name__ = 'Alinea.Phenomenal.models'

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

Phenomenal_models_strptime =  Factory(name='strptime',
                               authors='(C.Fournier)',
                               description='string -> date conversion',
                               category='',
                               nodemodule = 'alinea.phenomenal.models',
                               nodeclass = 'strptime',
                               inputs=[{'interface': ISequence, 'name': 'date strings', 'desc': 'Dates string sequence'},
                               {'interface': IStr, 'name': 'format', 'desc': 'format string', 'value': '%Y-%m-%d'}],                                                                      
                               outputs=[{'interface': None, 'name': 'dates'}],
                               )
__all__.append('Phenomenal_models_strptime')

Phenomenal_models_plantarea =  Factory(name='plant area',
                               authors='(C.Fournier)',
                               description='plant area estimation from pixel counts',
                               category='',
                               nodemodule = 'alinea.phenomenal.models',
                               nodeclass = 'plant_area',
                               inputs=[{'interface': ISequence, 'name': 'pixel counts', 'desc': 'sequuence of pixel counts'}],                                                                      
                               outputs=[{'interface': ISequence, 'name': 'Area'}],
                               )
__all__.append('Phenomenal_models_plantarea')

