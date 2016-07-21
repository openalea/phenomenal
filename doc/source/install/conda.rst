=====
Conda
=====

.. contents::

------------
From scratch
------------

Create virtual environment
--------------------------

Download & install miniconda at http://conda.pydata.org/miniconda.html

.. code:: shell


    conda create --name env_phenomenal python


    conda install numpy
    conda install scipy
    conda install networkx
    conda install vtk
    conda install scikit-image

    conda install opencv # not work on 64bit windows yet
    conda install -c menpo opencv=2.4.11

    # Visualizationconda
    conda install mayavi
    conda install matplotlib

    # Notebooks
    conda install jupyter
    conda install pandoc





