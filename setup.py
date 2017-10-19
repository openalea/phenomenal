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


setup(
    name="openalea.phenomenal",
    version="1.4.0",
    description="",
    long_description="",

    author="* Simon Artzet\n"
           "* Christian Fournier\n"
           "* Mielewczik Michael\n"
           "* Brichet Nicolas\n"
           "* Chopard Jerome\n"
           "* Christophe Pradal\n",

    author_email="",
    maintainer="Simon Artzet",
    maintainer_email="simon.artzet@gmail.com",

    url="https://gitlab.inria.fr/phenome/phenomenal",
    license="Cecill-C",
    keywords='',

    # package installation
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,

    # See MANIFEST.in
    include_package_data=True,
    )


