# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
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
# ==============================================================================
""" """

# ==============================================================================
from setuptools import setup
from setuptools.command.build_ext import build_ext
import numpy


class build_ext_with_numpy(build_ext):
    def finalize_options(self):
        super().finalize_options()
        # Add numpy include dir to all extensions
        print(numpy.get_include())
        for ext in self.extensions:
            ext.include_dirs.append(numpy.get_include())


setup(
    cmdclass={"build_ext": build_ext_with_numpy}
)