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
"""
"""
# ==============================================================================
import numpy
from Cython.Build import cythonize
from setuptools import setup, find_namespace_packages, Extension
# ==============================================================================

namespace = "openalea"
pkg_root_dir = 'src'
packages = find_namespace_packages(where='src', include=['openalea.*'])


extentions = [
    Extension('openalea.phenomenal.segmentation._c_skeleton',
        sources=['src/openalea/phenomenal/segmentation/src/skeleton.pyx',
             'src/openalea/phenomenal/segmentation/src/skel.cpp'],
        include_dirs=[numpy.get_include()],
        language="c++"),
    Extension('openalea.phenomenal.multi_view_reconstruction._c_mvr',
        sources=['src/openalea/phenomenal/multi_view_reconstruction/src/c_mvr.pyx',
                 'src/openalea/phenomenal/multi_view_reconstruction/src/integral_image.cpp'],
        include_dirs=[numpy.get_include()],
        language="c++")
        ]

version = {}
with open("src/openalea/phenomenal/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="openalea.phenomenal",
    version=version["__version__"],
    description="",
    long_description="",

    author="* Simon Artzet\n"
           "* Christian Fournier\n"
           "* Mielewczik Michael\n"
           "* Brichet Nicolas\n"
           "* Chopard Jerome\n"
           "* Christophe Pradal\n",

    author_email="simon.artzet@gmail.com",
    maintainer="Simon Artzet",
    maintainer_email="simon.artzet@gmail.com",

    url="https://github.com/openalea/phenomenal",
    license="Cecill-C",
    keywords='',

    # package installation
    packages=packages,
    package_dir={'': 'src'},
    zip_safe=False,
    ext_modules=cythonize(extentions),

    entry_points={
        "wralea": ["openalea.phenomenal = openalea.phenomenal_wralea", ],
    },

    # See MANIFEST.in
    include_package_data=True,
    )