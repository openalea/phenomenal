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
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
packages = pkgs
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

# List of top level wralea packages (directories with __wralea__.py)
# wralea_entry_points = ['%s = %s'%(pkg,namespace + '.' + pkg) for pkg in
# top_pkgs]

# dependencies to other eggs
setup_requires = ['openalea.deploy']

# if("win32" in sys.platform):
#    install_requires = []
# else:
#    install_requires = []
# install_requires = ['paramiko', 'scp', 'csv', 'psycopg2', 'openalea.deploy']
install_requires = []

# web sites where to find eggs
dependency_links = ['http://openalea.gforge.inria.fr/pi']

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
    setup_requires=setup_requires,
    install_requires=install_requires,
    dependency_links=dependency_links,

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data=True,

    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include
    #package_data = {'' : ['*.pyd', '*.so'],},
    share_dirs={'share': 'share'},
    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points={'wralea': ['phenomenal = alinea.phenomenal_wralea'],
        #'console_scripts': [
        #       'fake_script = openalea.fakepackage.amodule:console_script', ],
        # 'gui_scripts': [
        #      'fake_gui = openalea.fakepackage.amodule:gui_script',],
        #	'wralea': wralea_entry_points
        },
    )


