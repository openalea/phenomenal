# -*- python -*-
#
#       calibration_manuel.py :
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
import math

#       ========================================================================


class CameraConfiguration(object):
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


class Calibration(CameraConfiguration, object):
    def __init__(self):

        super(Calibration, self).__init__()

        # Dimension image
        # self.w = camera_config.w
        # self.h = camera_config.h

        # Box
        self.hbox = self.hSide / self.convSide
        self.cbox = self.cSide / self.convSide

        # X0, Y0, Z0
        self.xo = ((self.w / 2 - self.dleft) / self.convSide)
        self.yo = self.cbox / 2
        self.zo = ((self.h / 2 - (self.h - self.hSide)) / self.convSide)

        # echelle top au niveau du sol (pix / cm)
        convTop = self.convSide / self.cSide * self.cTop

        # XT, YT, ZT
        self.xt = (self.h / 2 - self.dleft_top) / convTop
        self.yt = (self.w / 2 - (self.w - self.dback - self.cTop)) / convTop
        self.zt = self.zo

        # facteur grandissement
        gamma = self.lcSide[1] / self.lcSide[0]
        self.pSide = self.convSide * (gamma - 1) / self.cbox

        gamma = self.lcTop[1] / self.lcTop[0]
        # echelle au niveau hcTop[1]
        cTop = self.lcTop[0] / self.lcSide[0] * self.convSide

        self.pTop = cTop * (gamma - 1) / (self.hcTop[0] - self.hcTop[1])

        # echelle au niveau 0
        self.convTopref = convTop + self.pTop * self.zo
        self.convSideref = self.convSide + self.pSide * self.cbox / 2
        self.rotationTop = - self.angTop

    def top_projection(self, position):
        # coordinates / optical center in real world
        x = position[0] - self.xt
        y = position[1] - self.yt
        z = position[2] - self.zt

        # scale at this distance
        conv = self.convTopref + z * self.pTop

        # image coordinates / optical center and real world oriented  axes
        ximo = x * conv
        yimo = y * conv
        # image coordinates
        xim = round(self.h / 2 + ximo)
        yim = round(self.w / 2 - yimo)

        return min(self.h, max(1, xim)), min(self.w, max(1, yim))

    def side_projection(self, position):
        # coordinates / optical center in real world
        x = position[0] - self.xo
        y = position[1] - self.yo
        z = position[2] - self.zo

        # scale at this distance
        conv = self.convSideref - y * self.pSide

        # image coordinates / optical center and real world oriented axes
        ximo = x * conv
        yimo = z * conv

        # EBI image coordinates
        xim = round(self.w / 2.0 + ximo)
        yim = round(self.h / 2.0 - yimo)

        return min(self.w, max(0, xim)), min(self.h, max(0, yim))

    def side_rotation(self, position, angle):

        t = - angle / 180.0 * math.pi
        cbox2 = self.cbox / 2.0
        sint = math.sin(t)
        cost = math.cos(t)

        x = position[0] - cbox2
        y = position[1] - cbox2

        tmp_x = cost * x - sint * y
        tmp_y = sint * x + cost * y

        return tmp_x + cbox2, tmp_y + cbox2, position[2]

    def project_point(self, point, angle):

        if angle == -1:
            return self.top_projection(point)
        else:
            if angle != 0:
                point = self.side_rotation(point, angle)

            x, y = self.side_projection(point)

            return x, y
