==========
Phenomenal
==========

A software framework for model-assisted analysis of high throughput
plant phenotyping data

.. contents::

What is Phenomenal ?
--------------------

Plant high-throughput phenotyping aims at capturing the genetic variability
of plant response to environmental factors for thousands of plants,
hence identifying heritable traits for genomic selection and predicting
the genetic values of allelic combinations in different environment.

This first implies the automation of the measurement of a large number of
traits to characterize plant growth, plant development and plant functioning.
It also requires a fluent and versatile interaction between data and
continuously evolving plant response models, that are essential in the analysis
of the marker x environment interaction and in the integration of processes
for predicting crop performance.

In the frame of the Phenome high throughput phenotyping infrastructure,
we develop **Phenomenal**. A software framework dedicated to the analysis of
high throughput phenotyping data and models.

Phenomenal currently consists of 2D image analysis workflows built with
standard image libraries (VTK, OpenCV, Scikit.Image), algorithms for 3D
reconstruction, segmentation and tracking of plant organs for maize
(under development), and workflows for estimation of light interception by
plants during their growth.


Installation
------------

.. toctree::

   ./install/index.rst

Documentation
-------------

Tutorial Jupyter Notebooks
''''''''''''''''''''''''''

Tutorial Jupyter Notebooks are available on the git repository in the folder
examples.

API References
''''''''''''''

.. toctree::

    ./references/index.rst


Authors
-------

.. include:: ../../AUTHORS.rst


License
-------

**Phenomenal** is released under a Cecill-C license.

.. note:: `Cecill-C <http://www.cecill.info/licences/
    Licence_CeCILL-C_V1-en.html>`_ license is a LGPL compatible license.
