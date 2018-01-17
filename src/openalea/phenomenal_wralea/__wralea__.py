
from openalea.core import Factory



__name__ = 'phenomenal.image'

__editable__ = True
__description__ = 'functions on images'
__license__ = 'CECILL-C'
__url__ = 'http://phenomenal.readthedocs.io/en/latest'
__alias__ = []
__version__ = "1.6.0"
__authors__ = "* Simon Artzet\n"
           "* Christian Fournier\n"
           "* Mielewczik Michael\n"
           "* Brichet Nicolas\n"
           "* Chopard Jerome\n"
           "* Christophe Pradal\n"

__institutes__ = 'INRA/INRIA/CIRAD'
__icon__ = ''


__all__ = [
    "phenomenal_image_thresholdMeanshift",
    "phenomenal_image_thresholdMeanshiftEnhance",

]



phenomenal_image_thresholdMeanshift = Factory(name='thresholdMeanshift',
                description='phenomenal.image binarization.',
                category='visualization, data processing',
                nodemodule='phenomenal_image',
                nodeclass='thresholdMeanshift',
                inputs=5, outputs=1, widgetmodule=None, widgetclass=None,
                lazy=False
)


phenomenal_image_thresholdMeanshiftEnhance = Factory(name='thresholdMeanshiftEnhance',
                description='phenomenal.image binarization.',
                category='visualization, data processing',
                nodemodule='phenomenal_image',
                nodeclass='thresholdMeanshiftEnhance',
                inputs=4, outputs=1, widgetmodule=None, widgetclass=None,
                lazy=False
)
