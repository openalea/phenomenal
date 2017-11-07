==============
Ubuntu (linux)
==============

Warning :This installation procedure is not fully tested, We strongly
recommand to install openalea.phenomenal with miniconda.

.. contents::

-----------------------
1. Install dependencies
-----------------------

Be sure opengl is installed on your machine

.. code:: shell

    sudo apt-get install freeglut3-dev


.. code:: shell

    # Basic
    sudo apt-get install python-setuptools python-numpy python-matplotlib
    python-scipy python-skimage python-opencv python-vtk

    # Optional
    sudo apt-get install python-nose ipython ipython-notebook

    # OpenAlea.Deploy
    git clone https://github.com/openalea/deploy
    cd deploys; python setup.py install; cd ..

    # OpenAlea.Core
    git clone https://github.com/openalea/core
    cd core; python setup.py install; cd ..

------------------------------
2. Install openalea.phenomenal
------------------------------

.. code:: shell

    git clone https://gitlab.inria.fr/phenome/phenomenal.git
    cd phenomenal; python setup.py install; cd ..

------------------------------------------------------------------
3. Test if installation is well installed (with nosetests package)
------------------------------------------------------------------

.. code:: shell

    cd phenomenal
    nosetests test
