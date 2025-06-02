# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


from openalea.phenomenal.optional_deps import require_dependency



# ==============================================================================


def show_values(list_values, list_color):
    plt = require_dependency('matplotlib.pyplot', 'viz')
    plt.figure()
    for values, color in zip(list_values, list_color):
        plt.plot(values, color)
    plt.show()


