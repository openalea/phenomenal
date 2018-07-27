==================================
Developer Install - Ubuntu (linux)
==================================

Warning : This installation procedure is not fully tested, We strongly
recommand to install openalea.phenomenal with miniconda.

.. contents::

-----------------------------
1. Install linux dependencies
-----------------------------

Be sure opengl is installed on your machine

.. code:: shell

    sudo apt-get update
    sudo apt-get install freeglut3-dev

2. Miniconda installation
-------------------------

Follow official website instruction to install miniconda :

http://conda.pydata.org/miniconda.html

3. Create virtual environment and activate it
.............................................

.. code:: shell

    conda create --name phenomenal python
    source activate phenomenal


4. Install dependencies with conda
----------------------------------

.. code:: shell

    conda install -c openalea/label/unstable -c openalea openalea.deploy openalea.core
    conda install numba numpy scikit-learn scikit-image scipy matplotlib networkx vtk opencv

    # Usefull tools for running example and documentation
    conda install -c conda-forge nose notebook sphinx sphinx_rtd_theme pandoc ipyvolume

    # On windows
    conda install pywin32 [win]

------------------------------
2. Install openalea.phenomenal
------------------------------

.. code:: shell

    git clone https://gitlab.inria.fr/phenome/phenomenal.git
    cd phenomenal; python setup.py develop --prefix=$CONDA_PREFIX; cd ..

------------------------------------------------------------------
3. Test if installation is well installed (with nosetests package)
------------------------------------------------------------------

.. code:: shell

    cd phenomenal
    nosetests test
