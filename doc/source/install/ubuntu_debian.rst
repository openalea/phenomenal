===============
Ubuntu & Debian
===============

.. contents::

------------
Requirements
------------

.. code:: shell

    #######
    # Basic
    sudo apt-get install python-setuptools
    sudo apt-get install python-numpy python-matplotlib python-nose
    sudo apt-get install ipython ipython-notebook

    #######
    # Image
    sudo apt-get install python-scipy python-skimage
    sudo apt-get install python-opencv
    sudo apt-get install python-vtk
    sudo apt-get install mayavi2

    #####################
    # OpenAlea dependency
    sudo apt-get install scons python-qt4

    #################
    # OpenAlea.Deploy
    git clone https://github.com/openalea/deploy
    cd deploys
    python setup.py develop

    #################
    # OpenAlea.Sconsx
    git clone https://github.com/openalea/sconsx
    cd sconsx
    python setup.py develop
    cd ..

    ###################
    # OpenAlea.OpenAlea
    git clone https://github.com/openalea/openalea
    cd openalea
    python multisetup.py develop
    cd ..

    ##############################
    # OpenAlea.OpenAlea-components
    git clone https://github.com/openalea/openalea-components
    cd openalea-components
    python multisetup.py develop
    cd ..

--------------------------------------------------------------------------------

----------
Phenomenal
----------

.. code:: shell

    git clone https://<username>@scm.gforge.inria.fr/authscm/<username>/git/phenomenal/phenomenal.git
    cd phenomenal
    python setup.py develop
    cd ..
