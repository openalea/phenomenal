.. image:: https://travis-ci.org/openalea/phenomenal.svg?branch=master
    :target: https://travis-ci.org/openalea/phenomenal
    :alt: Travis Status


.. image::  https://ci.appveyor.com/api/projects/status/k7up7iy2ur2wmipx/branch/master?svg=true
    :target: https://ci.appveyor.com/project/artzet/phenomenal
    :alt: Appveyor Status

.. image:: https://readthedocs.org/projects/phenomenal/badge/?version=latest
    :target: https://phenomenal.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status



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

Tutorials are available in the example folder as a Jupyter Notebook.

Note :

- To install jupyter notebook (conda install -c conda-forge notebook ipyvolume)

To replay notebook tutorial launch with the following command

.. code:: shell

    jupyter notebook

=================================================
Installation with Miniconda (Windows, linux, OSX)
=================================================

Miniconda installation
----------------------

Follow official website instruction to install miniconda :

http://conda.pydata.org/miniconda.html

1. Install conda-build if not already installed
...............................................

.. code:: shell

    conda install conda-build

2. Create virtual environment and activate it
.............................................

.. code:: shell

    conda create --name phenomenal python
    source activate phenomenal

3. Build and install openalea.phenomenal package
................................................

.. code:: shell

    cd phenomenal/build_tools/conda
    conda build -c conda-forge -c openalea .
    conda install -c conda-forge -c openalea --use-local openalea.phenomenal

(Optional) Install several package managing tools :

.. code:: shell

    conda install -c conda-forge notebook nose sphinx sphinx_rtd_theme pandoc coverage ipyvolume nbconvert

Authors
-------

* Artzet	    Simon
* Brichet	    Nicolas
* Chopard       Jerome
* Mielewczik    Michael
* Fournier	    Christian
* Pradal        Christophe

Mainteners
----------

* Artzet	    Simon
* Fournier	    Christian
* Pradal        Christophe

