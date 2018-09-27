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
from setuptools import setup, find_packages, Extension, Command
# ==============================================================================

namespace = "openalea"
pkg_root_dir = 'src'
packages = [pkg for pkg in find_packages(pkg_root_dir)]
top_pkgs = [pkg for pkg in packages if len(pkg.split('.')) <= 2]
package_dir = dict([('', pkg_root_dir)] +
                   [(pkg, pkg_root_dir + "/" + pkg.replace('.', '/'))
                    for pkg in top_pkgs])


extentions = [Extension(
    'openalea.phenomenal.segmentation._c_skeleton',
    sources=['src/openalea/phenomenal/segmentation/src/skeleton.pyx',
             'src/openalea/phenomenal/segmentation/src/skel.cpp'],
    include_dirs=[numpy.get_include()],
    language="c++")]

setup(
    name="openalea.phenomenal",
    version="1.6.1",
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
    package_dir=package_dir,
    zip_safe=False,
    ext_modules=cythonize(extentions),

    entry_points={
        "wralea": ["openalea.phenomenal = openalea.phenomenal_wralea", ],
    },

    # See MANIFEST.in
    include_package_data=True,
    )
