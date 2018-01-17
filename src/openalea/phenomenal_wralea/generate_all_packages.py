from os.path import abspath
from openalea.core import UserPackage, Factory
from setuptools import find_packages

list_pkg = find_packages()
list_pkg.remove('demo')

list_mod=[]
list_name=["openalea.phenomenal."+x for x in list_pkg]

for el in list_name:
    list_mod.append(__import__(el, fromlist=['']))




def functions(module, path_mod):
    """ Get all the factories of the module module.
    """

    name = module.__name__
    _all = module.__all__

    funs = [x for x in _all if callable(module.__getattribute__(x))]

    metainfo = dict(authors='Me', license='CeCILL-C', version='1.6.0')

    pkg = UserPackage(name=name, metainfo=metainfo, path=abspath(path_mod))

    for func_name in funs:
        fact = Factory(name=func_name, 
                       category=name, 
                       nodemodule=name,
                       nodeclass=func_name)

        pkg.add_factory(fact)
    
    pkg.write()

    return pkg

#TODO
#fix wralea ne fonctionne pas
#l'appliquer dans chaque dossier

def fix_wralea(path_mod):
    import __wralea__
    all_ = __wralea__.__all__

    d = dict((x, x.replace('.', '_')) for x in all_)
    path_wralea = path_mod + '/__wralea__.py'
    
    with open(path_wralea, 'r') as f:
        s = f.read()

    for x, y in d.iteritems():
        s = s.replace(x, y)

    with open(path_wralea, 'w') as f:
        f.write(s)

   

    
if __name__ =='__main__':
    for module in list_mod:
        functions(module, module.__name__.rsplit('.', 1)[-1])
        fix_wralea(module.__name__.rsplit('.', 1)[-1])



