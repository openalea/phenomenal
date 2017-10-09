[![build status](https://gitlab.inria.fr/phenome/phenomenal/badges/master/build.svg)](https://gitlab.inria.fr/phenome/phenomenal/commits/master)
[![coverage report](https://gitlab.inria.fr/phenome/phenomenal/badges/master/coverage.svg)](https://gitlab.inria.fr/phenome/phenomenal/commits/master)


==========
Phenomenal
==========

A software framework for model-assisted analysis of high throughput
plant phenotyping data

**Phenomenal** is released under a `Cecill-C <http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html>`_ license.


.. contents::

=============
Documentation
=============

The documentation is available at `<https://phenomenal.readthedocs.io>`_

Tutorials is available in the example folder as a Jupyter Notebook.

===========================
Installation with Miniconda
===========================

Miniconda installation
----------------------

Follow official website instruction to install miniconda :

http://conda.pydata.org/miniconda.html

On Linux / Ubuntu / MacOS
-------------------------

Create virtual environment and activate it
..........................................

.. code:: shell

    conda create --name phenomenal python
    source activate phenomenal

Dependencies install
....................

.. code:: shell

    conda install -c conda-forge numpy matplotlib opencv scikit-image
    conda install -c openalea openalea.deploy openalea.core

(Optional) Package managing tools :

.. code:: shell

    conda install -c conda-forge notebook nose sphinx sphinx_rtd_theme pandoc


Phenomenal install
................

.. code:: shell

    git clone https://gitlab.inria.fr/phenome/phenomenal.git
    cd phenomenal
    python setup.py install --prefix=$CONDA_PREFIX

On Windows
----------

Create virtual environment and activate it
..........................................

.. code:: shell

    conda create --name phenomenal python
    activate phenomenal

Dependencies install
....................

.. code:: shell

    conda install -c conda-forge numpy matplotlib scikit-image opencv pywin32
    conda install -c openalea openalea.deploy openalea.core

(Optional) Package managing tools :

.. code:: shell

    conda install -c conda-forge notebook nose sphinx sphinx_rtd_theme pandoc


Phenomenal install
................

.. code:: shell

    git clone https://gitlab.inria.fr/phenome/phenomenal.git
    cd phenomenal
    python setup.py install --prefix=%CONDA_PREFIX%


Authors
-------

* Artzet	    Simon		(simon.artzet@gmail.com)
* Fournier	    Christian	(christian.fournier@supagro.inra.fr)
* Brichet	    Nicolas		(brichet@supagro.inra.fr)
* Chopard       Jerome      (revesansparole@gmail.com)
* Mielewczik	Michael
