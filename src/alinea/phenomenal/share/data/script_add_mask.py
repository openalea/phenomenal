# -*- python -*-
#
#       binarization.py: Module Description
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
#       =======================================================================

""" Binarization routines for PhenoArch/ images
"""

#       =======================================================================
#       External Import
import cv2


#       =======================================================================
#       Local Import

#       ====================================================================
#       Code

# orange_band_mask = masksideview-orange_optimized2.png
# side_panels_mask = mask-sideview-SidePanel.png

img1 = cv2.imread("./masksideview-orange_optimized2.png",
                  cv2.CV_LOAD_IMAGE_GRAYSCALE)

img2 = cv2.imread("./mask-sideview-SidePanel.png",
                  cv2.CV_LOAD_IMAGE_GRAYSCALE)

img = cv2.add(img1, img2)

cv2.imwrite("./img_out.png", img, cv2.CV_LOAD_IMAGE_GRAYSCALE)