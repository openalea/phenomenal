# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import math
# ==============================================================================

__all__ = ["EnvironmentCamera",
           "CalibrationCameraManual"]

# ==============================================================================


class EnvironmentCamera(object):
    def __init__(self):
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


class CalibrationCameraManual(object):
    def __init__(self, env_feat):

        # ======================================================================
        # Dimension image
        self.width_image = env_feat.w
        self.height_image = env_feat.h

        w = self.width_image
        h = self.height_image
        w2 = w / 2
        h2 = h / 2

        # ======================================================================
        # Box
        self.hbox = env_feat.hSide / env_feat.convSide
        self.cbox = env_feat.cSide / env_feat.convSide

        # ======================================================================
        # X0, Y0, Z0
        self.xo = ((w2 - env_feat.dleft) / env_feat.convSide)
        self.yo = self.cbox / 2
        self.zo = ((h2 - (h - env_feat.hSide)) / env_feat.convSide)

        # ======================================================================
        # Top scale ground level (pix / cm)
        conv_top = env_feat.convSide / env_feat.cSide * env_feat.cTop

        # XT, YT, ZT
        self.xt = (h2 - env_feat.dleft_top) / conv_top
        self.yt = ((w2 - (w - env_feat.dback - env_feat.cTop)) / conv_top)
        self.zt = self.zo

        # ======================================================================
        # Enlargement factor
        gamma = env_feat.lcSide[1] / env_feat.lcSide[0]
        self.pSide = env_feat.convSide * (gamma - 1) / self.cbox

        # ======================================================================
        # hcTop[1] scale level
        cTop = (env_feat.lcTop[0] / env_feat.lcSide[0] * env_feat.convSide)
        gamma = env_feat.lcTop[1] / env_feat.lcTop[0]

        self.pTop = cTop * (gamma - 1) / (env_feat.hcTop[0] - env_feat.hcTop[1])

        # ======================================================================
        # Scale level 0
        self.conv_top_ref = conv_top + self.pTop * self.zo
        self.conv_side_ref = env_feat.convSide + self.pSide * self.cbox / 2
        self.rotationTop = - env_feat.angTop

    def top_projection(self, position):
        # coordinates / optical center in real world
        x = position[0] - self.xt
        y = position[1] - self.yt
        z = position[2] - self.zt

        # scale at this distance
        conv = self.conv_top_ref + z * self.pTop

        # image coordinates / optical center and real world oriented  axes
        ximo = x * conv
        yimo = y * conv
        # image coordinates
        xim = round(self.height_image / 2 + ximo)
        yim = round(self.width_image / 2 - yimo)

        return (min(self.height_image, max(1, xim)),
                min(self.width_image, max(1, yim)))

    def side_projection(self, position):
        # coordinates / optical center in real world
        x = position[0] - self.xo
        y = position[1] - self.yo
        z = position[2] - self.zo

        # scale at this distance
        conv = self.conv_side_ref - y * self.pSide

        # image coordinates / optical center and real world oriented axes
        ximo = x * conv
        yimo = z * conv

        # EBI image coordinates
        xim = round(self.width_image / 2.0 + ximo)
        yim = round(self.height_image / 2.0 - yimo)

        return (min(self.width_image, max(0, xim)),
                min(self.height_image, max(0, yim)))

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

    def get_projection(self, angle):
        return lambda pt3d: self.project_point(pt3d, angle)
