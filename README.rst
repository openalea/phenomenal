
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

Create virtual environment and activate it
..........................................

.. code:: shell

    conda create --name phenomenal python
    source activate phenomenal

Dependencies install
....................

.. code:: shell

    cd phenomenal/build_tools/conda
    conda build -c conda-forge -c openalea .
    conda install -c conda-forge -c openalea --use-local openalea.phenomenal

(Optional) Package managing tools :

.. code:: shell

    conda install -c conda-forge notebook nose sphinx sphinx_rtd_theme pandoc



Authors
-------

* Artzet	    Simon		(simon.artzet@gmail.com)
* Fournier	    Christian	(christian.fournier@supagro.inra.fr)
* Brichet	    Nicolas		(brichet@supagro.inra.fr)
* Chopard       Jerome      (revesansparole@gmail.com)
* Mielewczik	Michael
