===================
Installation on MAC
===================

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

.. code:: shell

    conda install -c menpo mayavi opencv qt==4.8.6 matplotlib networkx
    scikit-image scipy==0.17

    conda install jupyter nose coverage


Install Phenomenal
..................

.. code:: shell

    git clone https://<username>@scm.gforge.inria.fr/authscm/<username>/git/phenomenal/phenomenal.git
    cd phenomenal
    python setup.py develop --prefix=$CONDA_PREFIX
    cd ..


