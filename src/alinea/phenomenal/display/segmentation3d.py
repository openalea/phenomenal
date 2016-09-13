# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import numpy
import mayavi.mlab
# ==============================================================================


def plot_plane(plane, point):

    def get_point_of_planes(normal, node, radius=5):
        a, b, c = normal
        x, y, z = node

        d = a * x + b * y + c * z

        xx = numpy.linspace(x - radius, x + radius, radius * 2)
        yy = numpy.linspace(y - radius, y + radius, radius * 2)

        xv, yv = numpy.meshgrid(xx, yy)

        zz = - (a * xv + b * yv - d) / c

        return xv, yv, zz

    x, y, z = point
    a, b, c, d = plane

    a = float(round(a, 4) * 1000)
    b = float(round(b, 4) * 1000)
    c = float(round(c, 4) * 1000)

    print x, y, z, a, b, c, d

    d = float(max(a, b, c, 1))

    mayavi.mlab.quiver3d(float(x), float(y), float(z),
                         a / d, b / d, c /d,
                         line_width=1.0,
                         scale_factor=0.1)

    xx, yy, zz = get_point_of_planes((a, b, c), (x, y, z), radius=40)
    mayavi.mlab.mesh(xx, yy, zz)


