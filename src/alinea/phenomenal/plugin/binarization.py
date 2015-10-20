# -*- python -*-
#
#       binarization.py :
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
#       ========================================================================

#       ========================================================================
#       External Import
import openalea.core

#Need to install pyqode, pyqode core, pyqore qt

#       ========================================================================
#       Local Import
import alinea.phenomenal.plugin.authors

#       ========================================================================
#       Code

class AlineaPhenomenalBinarizationPlugin(object):
    __plugin__ = True
    modulename = "alinea.phenomenal.binarization"
    objectname = "binarization"

    implement = 'alinea_phenomenal'
    name = 'alinea_phenomenal_binarization'
    label = 'Alinea Phenomenal Binarization'

    param1 = dict()
    param1['name'] = 'images'
    param1['interface'] = 'IDict'
    # param1['default'] = dict() or None
    param1['label'] = 'Images Dict'

    param2 = dict()
    param2['name'] = 'factor'
    # param2['interface'] = ''
    # param1['default'] = dict() or None
    param2['label'] = 'Factor of Binarization'

    param3 = dict()
    param3['name'] = 'methods'
    param3['interface'] = 'IStr'
    # param1['default'] = dict() or None
    param3['label'] = 'Methods name'

    inputs = [param1, param2, param3]

    param4 = dict()
    param4['name'] = 'images'
    param4['interface'] = 'IDict'
    param4['label'] = 'Images Dict'

    outputs = [param4]

    authors = [alinea.phenomenal.plugin.authors.artzet_simon,
               alinea.phenomenal.plugin.authors.fournier_christian,
               alinea.phenomenal.plugin.authors.brichet_nicolas,
               alinea.phenomenal.plugin.authors.mielewczik_michael]

    tags = ['Alinea', 'Phenomenal', 'Binarization', '2d']

    description = ''
#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    pass
