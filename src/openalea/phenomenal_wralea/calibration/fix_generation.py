

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
    fix_wralea()
