# -*- python -*-
#
#       setup.py : Module Description
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

"""
Write the doc here...
"""

__revision__ = "$Id: $"

#       =======================================================================
#       External Import
import sys
import os

#       =======================================================================
#       Local Import
from setuptools import setup, find_packages
from openalea.deploy.metainfo import read_metainfo

# Reads the metainfo file
metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))

# Packages list, namespace and root directory of packages

pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir)]
top_pkgs = [pkg for pkg in pkgs if len(pkg.split('.')) < 2]
packages = pkgs
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

# List of top level wralea packages (directories with __wralea__.py)
# wralea_entry_points = ['%s = %s'%(pkg,namespace + '.' + pkg) for pkg in
# top_pkgs]


setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords='',

    # package installation
    packages=packages,
    package_dir=package_dir,

    # Namespace packages creation by deploy
    #namespace_packages = [namespace],
    #create_namespaces = False,
    zip_safe=False,

    # Dependencies
    setup_requires=['openalea.deploy'],
    install_requires=[],
    dependency_links=['http://openalea.gforge.inria.fr/pi'],

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data=True,

    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include
    #package_data = {'' : ['*.pyd', '*.so'],},
    share_dirs={'share': './share'},
    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points={
        'wralea': ['phenomenal = alinea.phenomenal_wralea'],
        'openalea.image': ['AlineaPhenomenalBinarizationPlugin =  alinea.phenomenal.plugin.binarization'],},
    )


