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

.. code:: shell

    conda install numpy matplotlib scipy networkx scikit-image scikit-learn pandas
    conda install -c menpo opencv mayavi wxpython
    conda install jupyter nose coverage
    conda install -c openalea openalea.deploy openalea.core


Install Phenomenal
------------------

.. code:: shell

    git clone https://<username>@scm.gforge.inria.fr/authscm/<username>/git/phenomenal/phenomenal.git
    cd phenomenal
    python setup.py develop --prefix=%CONDA_PREFIX%
    cd ..

