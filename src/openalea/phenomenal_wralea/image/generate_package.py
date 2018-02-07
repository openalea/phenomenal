from os.path import abspath
from openalea.core import UserPackage, Factory

import openalea.phenomenal.image as img


def functions(module):
    """ Get all the factories of the module module.
    """

    name = module.__name__
    _all = module.__all__

    funs = [x for x in _all if callable(module.__getattribute__(x))]

    metainfo = dict(authors='Me', license='CeCILL-C', version='1.6.0')

    pkg = UserPackage(name=name, metainfo=metainfo, path=abspath('.'))

    for func_name in funs:
        fact = Factory(name=func_name, 
                       category='Image', 
                       nodemodule=name,
                       nodeclass=func_name)

        pkg.add_factory(fact)
    
    pkg.write()

    return pkg

def fix_wralea():
    import __wralea__
    all_ = __wralea__.__all__

    d = dict((x, x.replace('.', '_')) for x in all_)

    f = open('__wralea__.py', 'r')
    s = f.read()
    f.close()

    for x, y in d.iteritems():
        s = s.replace(x, y)
    
    f = open('__wralea__.py', 'w')
    f.write(s)
    f.close()

    
if __name__ =='__main__':
    functions(img)
    fix_wralea()

