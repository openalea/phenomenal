.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1436634.svg
   :target: https://doi.org/10.5281/zenodo.1436634

.. image:: https://anaconda.org/openalea/openalea.phenomenal/badges/license.svg
    :target: http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
    :alt: Licence Status

.. image:: https://anaconda.org/openalea/openalea.phenomenal/badges/platforms.svg
    :target: https://anaconda.org/OpenAlea/openalea.phenomenal/files
    :alt: Platform supported Status

.. image:: https://anaconda.org/openalea/openalea.phenomenal/badges/version.svg
    :target: https://anaconda.org/OpenAlea/openalea.phenomenal
    :alt: The last version

.. image:: https://travis-ci.org/openalea/phenomenal.svg?branch=master
    :target: https://travis-ci.org/openalea/phenomenal
    :alt: Travis Status

.. image::  https://ci.appveyor.com/api/projects/status/k7up7iy2ur2wmipx/branch/master?svg=true
    :target: https://ci.appveyor.com/project/artzet-s/phenomenal
    :alt: Appveyor Status

.. image:: https://readthedocs.org/projects/phenomenal/badge/?version=latest
    :target: https://phenomenal.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://mybinder.org/badge.svg
    :target: https://mybinder.org/v2/gh/openalea/phenomenal/master?filepath=examples
    :alt: Launch interactive phenomenal notebook with myBinder service

==========
Phenomenal
==========

A software framework for model-assisted analysis of high throughput
plant phenotyping data

**Phenomenal** is released under a `Cecill-C <http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html>`_ licence.

.. contents::

=============
Citation
=============

Please, cite the software, if you are using for your research.

      @misc{artzet2018,
        author       = {Simon Artzet and
                        Nicolas Brichet and
                        Jerome Chopard and
                         Michael Mielewczik and
                         Christian Fournier and
                        Christophe Pradal},
        title        = {OpenAlea.Phenomenal: A Workflow for Plant Phenotyping},
        month        = sep,
        year         = 2018,
        doi          = {10.5281/zenodo.1436634},
        url          = {https://doi.org/10.5281/zenodo.1436634}
      }

============
Installation
============

First install conda : https://docs.conda.io/en/latest/index.html

User
----

Create a new environment with phenomenal installed in there :

.. code:: shell

    conda create -n phm -c conda-forge -c openalea openalea.phenomenal
    conda activate phm

In a existing environment :

.. code:: shell

    conda install -c conda-forge -c openalea openalea.phenomenal

(Optional) Test your installation :

.. code

    conda install -c conda-forge pytest
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal/test; pytest

From source
-----------

.. code::

    # Install dependency with conda
    conda create -n phm -c conda-forge python=3
    conda activate phm
    conda install -c conda-forge -c openalea cython numpy numba scipy scikit-image scikit-learn networkx=2.3 opencv matplotlib vtk pytest

    # Load phenomenal and install
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal
    python setup.py develop

    # (Optional) Test your installation
    cd test; pytest


=============
Documentation
=============

Complete documentation is available at `<https://phenomenal.readthedocs.io>`_

========
Tutorial
========

Tutorials are available in the example folder as a Jupyter Notebook.

You can try out with binder: https://mybinder.org/v2/gh/openalea/phenomenal/master?filepath=examples

=======
Authors
=======

* Artzet	    Simon
* Brichet	    Nicolas
* Chopard       Jerome
* Mielewczik    Michael
* Fournier	    Christian
* Pradal        Christophe

Maintainers
-----------

* Artzet	    Simon
* Fournier	    Christian
* Pradal        Christophe

