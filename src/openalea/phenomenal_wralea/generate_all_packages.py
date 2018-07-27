# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
import os.path
import setuptools

import openalea.core
# ==============================================================================


def functions(module, module_base_name, name_package=None):
    """ Get all the factories of the module module.
    """

    if name_package is None:
        name_package = module.__name__
    _all = module.__all__

    funs = [x for x in _all if callable(module.__getattribute__(x))]

    metainfo = dict(authors='Simon Artzet et al.',
                    license='CeCILL-C',
                    version='1.6.0')

    pkg = openalea.core.UserPackage(name=name_package,
                                    metainfo=metainfo,
                                    path=os.path.abspath(module_base_name))

    for func_name in funs:
        fact = openalea.core.Factory(name=func_name,
                                     category=name_package,
                                     nodemodule=module.__name__,
                                     nodeclass=func_name)

        pkg.add_factory(fact)
    
    pkg.write()

    return pkg


def main():
    list_pkg = setuptools.find_packages()
    list_pkg.remove('demo')
    list_pkg.remove('phenoarch')

    module_names = ["openalea.phenomenal.{}".format(x) for x in list_pkg]
    modules = [__import__(name, fromlist=['']) for name in module_names]

    for module in modules:
        functions(module, module.__name__.rsplit('.', 1)[-1])

    module = __import__("openalea.phenomenal_wralea.phenoarch", fromlist=[''])
    functions(module,
              module.__name__.rsplit('.', 1)[-1],
              name_package="openalea.phenomenal.phenoarch")


if __name__ =='__main__':
    main()
