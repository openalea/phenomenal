============
Installation
============

You must use conda environment : https://docs.conda.io/en/latest/index.html

Users
=====

Create a new environment with phenomenal installed in there
-----------------------------------------------------------

.. code-block:: bash

    mamba create -n phm -c openalea3 -c conda-forge openalea.phenomenal
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

Editable mode install
---------------------

.. code-block:: bash

    # Clone phenomenal
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal

    # Solution 1: Build env from scratch (mostly use pip dependencies)
    mamba env create -f conda/environment.yml
    mamba activate phenomenal_dev

    # Solution 2: use an existing env (mostly use conda dependencies)
    mamba activate my_env
    mamba install --only-deps -c openalea3 -c conda-forge openalea.phenomenal
    pip install -e .[doc,test]

    # (Optional) Test your installation
    cd test; pytest

