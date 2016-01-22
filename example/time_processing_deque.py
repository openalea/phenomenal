# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
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
import collections
import time
# ==============================================================================


def function_1(values=10000):
    d = collections.deque(range(values))

    for element in d:
        pass


def function_2(values=10000):
    d = collections.deque(range(values))
    while True:
        try:
            element = d.popleft()
        except IndexError:
            break

if __name__ == '__main__':

    v = 10000000

    t0 = time.time()
    function_1(values=v)
    print time.time() - t0

    t0 = time.time()
    function_2(values=v)
    print time.time() - t0


