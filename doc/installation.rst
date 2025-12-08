============
Installation
============

You must use conda environment : https://docs.conda.io/en/latest/index.html

Users
=====

Create a new environment with phenomenal installed in there
-----------------------------------------------------------

.. code-block:: bash

    mamba create -n phm -c openalea3 -c conda-forge  openalea.phenomenal
    mamba activate phm

Install phenomenal in a existing environment
---------------------------------------------

.. code-block:: bash

    mamba install -c openalea3 -c conda-forge openalea.phenomenal

(Optional) Test your installation
---------------------------------

.. code-block:: bash

    mamba install -c conda-forge pytest
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal/test; pytest

Developers
==========

Install From source
-------------------

.. code-block:: bash

    # Clone phenomenal and install
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal

    # Install dependency with conda
    mamba env create -n phm -f conda/environment.yml
    mamba activate phm

    # (Optional) Test your installation
    cd test; pytest

