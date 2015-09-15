# -*- python -*-
#
#       models.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
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

"""
Models for  estimation of biological traits from image analysis
"""

#       ========================================================================
#       External Import
import datetime
import numpy

#       ========================================================================

def strptime(dateseq, format='%Y-%m-%d'):
    """
    string -> date conversion
    """
    return map(lambda x: datetime.datetime.strptime(x, format), dateseq)


def plant_area(pixel_counts, a=3.261011e-06, b=0.04240879):
    """
    Plant area estimation from pixels counts
    """
    pix = numpy.array(pixel_counts)
    return a * pix + b