=======
Windows
=======

.. contents::

------------
Requirements
------------

.. code:: shell

    #######
    # Basic
    pip install numpy matplotlib ipython ipython[notebook] nose scons
    pip install scipy
    pip install scikit-image


    ############################################################################
    # Download Scipy, OpenCv, VTK, Mayavi, PyQt4, ... wheels
    # on http://www.lfd.uci.edu/~gohlke/pythonlibs/ and install it like this :
    pip install *.whl

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
