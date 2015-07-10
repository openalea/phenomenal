# -*- python -*-
#
#       calibration_class: Module Description
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


class CameraConfiguration:
    def __init__(self):
        #   ===================================================================
        #   Default value

        # Dimension image
        self.w = 2056
        self.h = 2454

        # Angle conveyor belt/horizontale (degrees) sur TopImage
        self.angTop = 0.6

        # Dimension pixel de l'arrete du plancher vu de dessus
        self.cTop = 1650

        # Distance pixel bord gauche image -> bord gauche boite sur image top
        self.dleft_top = 375

        # Distance pixel bord haut image -> bord plancher au fond sur image top
        self.dback = 228

        # Hauteurs (cm) du damier pour mesure effet perspective vu Top
        self.hcTop = (4, 180)

        # Grande largeur pixels du damier aux hauteurs de calibration
        self.lcTop = (384, 720)

        # Dimension pixel de l'arrete du plancher au fond de la cabine sur
        # photos side
        self.cSide = 1166

        # Distance pixel sol -> haut image au niveau du fond de la cabine
        self.hSide = 1957

        # Distance pixel bord gauche image -> bord gauche boite au niveu du
        # fond de la cabine
        self.dleft = 446

        # Distance pixel sol fond de cabine, sol devanture de cabine
        self.dhSide = 238

        # Grande largeur pixel du damier
        self.lcSide = (209.0 * (9.0 / 7.0), 277.0 * (9.0 / 7.0))

        # Conversion cm -> pixel pour image side (pixel careau noir / cm
        # careau noir) sur le fond
        self.convSide = 30 / 3.95

    def print_value(self):
        print 'Dimension image (w, h): ', self.w, ' , ', self.h
        print 'Angle conveyor', self.angTop
        print '', self.cTop
        print '', self.dleft_top
        print '', self.dback
        print '', self.hcTop
        print '', self.lcTop
        print '', self.cSide
        print '', self.hSide
        print '', self.dleft
        print '', self.dhSide
        print '', self.lcSide
        print '', self.convSide


class Calibration:
    def __init__(self, camera_config):
        # Dimension image
        self.w = camera_config.w
        self.h = camera_config.h

        # Box
        self.hbox = camera_config.hSide / camera_config.convSide
        self.cbox = camera_config.cSide / camera_config.convSide

        # X0, Y0, Z0
        self.xo = ((camera_config.w / 2 - camera_config.dleft) /
                   camera_config.convSide)

        self.yo = self.cbox / 2

        self.zo = ((camera_config.h / 2 - (camera_config.h -
                                           camera_config.hSide)) /
                   camera_config.convSide)

        # echelle top au niveau du sol (pix / cm)
        convTop = camera_config.convSide / camera_config.cSide * camera_config.cTop

        # XT, YT, ZT
        self.xt = (camera_config.h / 2 - camera_config.dleft_top) / convTop
        self.yt = (camera_config.w / 2 - (
        camera_config.w - camera_config.dback - camera_config.cTop)) / convTop
        self.zt = self.zo


        # facteur grandissement
        gamma = camera_config.lcSide[1] / camera_config.lcSide[0]
        self.pSide = camera_config.convSide * (gamma - 1) / self.cbox

        gamma = camera_config.lcTop[1] / camera_config.lcTop[0]
        cTop = camera_config.lcTop[0] / camera_config.lcSide[
            0] * camera_config.convSide  # echelle au niveau hcTop[1]

        self.pTop = cTop * (gamma - 1) / (camera_config.hcTop[0] -
                                          camera_config.hcTop[1])

        # echelle au niveau 0
        self.convTopref = convTop + self.pTop * self.zo
        self.convSideref = camera_config.convSide + self.pSide * self.cbox / 2
        self.rotationTop = - camera_config.angTop

    def print_value(self):
        print 'w, h', self.w, self.h
        print 'hbox', self.hbox
        print 'cbox', self.cbox
        print 'X0', self.xo
        print 'Y0', self.yo
        print 'Z0', self.zo
        print 'XT', self.xt
        print 'YT', self.yt
        print 'ZT', self.zt
        print 'pSide', self.pSide
        print 'pTop', self.pTop
        print 'convTopRef', self.convTopref
        print 'convSideRef', self.convSideref
        print 'rotationTop', self.rotationTop
