======================
Installation on UBUNTU
======================

.. contents::

Download an Install Conda
-------------------------

See : http://conda.pydata.org/miniconda.html


Create virtual environment
..........................

.. code:: shell

    conda create --name phenomenal python

    source activate phenomenal


Install Requirements:
.....................

Core :


conda install -c menpo mayavi opencv qt==4.8.6 matplotlib networkx scikit-image
conda install jupyter nose
conda install -c openalea.grapheditor
conda install -c openalea vplants.plantgl
conda install scipy==0.17

.. code:: shell

    conda install numpy, scipy, networkx, vtk, scikit-image, opencv
    conda install -c openalea openalea.deploy openalea.core openalea.grapheditor

Visualization :

.. code:: shell

    conda install mayavi
    conda install matplotlib

Notebooks :

.. code:: shell

    conda install jupyter

Tests tools:

.. code:: shell

    conda install nose, coverage

Install Phenomenal
..................

.. code:: shell

    git clone https://<username>@scm.gforge.inria.fr/authscm/<username>/git/phenomenal/phenomenal.git
    cd phenomenal
    python setup.py develop --prefix=$CONDA_PREFIX
    cd ..
