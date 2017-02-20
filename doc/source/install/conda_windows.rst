======================
Installation on Window
======================

.. contents::

Download an Install Conda
-------------------------

See : http://conda.pydata.org/miniconda.html

Create virtual environment
--------------------------

.. code:: shell

    conda create --name phenomenal python

    activate phenomenal


Install Requirements:
---------------------

Core :

.. code:: shell

    conda install numpy, scipy, networkx, vtk, scikit-image
    conda install -c menpo opencv

Visualization :

.. code:: shell

    conda install -c menpo mayavi
    conda install matplotlib

Notebooks :

.. code:: shell

    conda install jupyter

Tests tools:

.. code:: shell

    conda install nose, coverage


Install Phenomenal
------------------

.. code:: shell

    git clone https://<username>@scm.gforge.inria.fr/authscm/<username>/git/phenomenal/phenomenal.git
    cd phenomenal
    python setup.py develop --prefix=%CONDA_PREFIX%
    cd ..

