# -*- python -*-
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
# ==============================================================================
"""
"""
# ==============================================================================
from setuptools import setup, find_packages
# ==============================================================================

# Packages list, namespace and root directory of packages

pkg_root_dir = 'src'
namespace = "alinea"

packages = [package for package in find_packages(pkg_root_dir)]
top_packages = [package for package in packages if len(package.split('.')) < 2]

package_dir = dict()
package_dir[''] = pkg_root_dir

for package in top_packages:
    package_dir[namespace + "." + package] = pkg_root_dir + "/" + package

setup(
    name="phenomenal",
    version="1.4.0",
    description="",
    long_description="",
    author="",
    author_email="",
    url="http://openalea.gforge.inria.fr",
    license="Cecill-C",
    keywords='',

    # package installation
    packages=packages,
    package_dir=package_dir,
    zip_safe=False,

    # Dependencies
    setup_requires=[],
    install_requires=[],
    dependency_links=['http://openalea.gforge.inria.fr/pi'],

    # # Eventually include data in your package
    # # (flowing is to include all versioned files other than .py)
    #include_package_data=True,

    package_data={'data': ['*']},
    # share_dirs={'share': './share'},
    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points={
        'wralea': ['phenomenal = alinea.phenomenal_wralea'],
        'openalea.image': ['AlineaPhenomenalBinarizationPlugin =  alinea.phenomenal.plugin.binarization'],},
    )


