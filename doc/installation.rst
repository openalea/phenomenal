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

    # (windows only) install VisualStudio Build Tools
    # (macos only) install Xcode Command Line Tools

    # Clone phenomenal
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal

    # Solution 1: Build env from scratch
    mamba create -n phenomenal_dev -f conda/environment.yml -f conda/run_deps.yml -f conda/doc_deps.yml
    mamba activate phenomenal_dev
    pip install -e . --no-build-isolation

    # Solution 2: use an existing env
    mamba activate my_env
    mamba install -c openalea3 -c conda-forge -f conda/run_deps.yml -f conda/doc_deps.yml
    mamba install -c conda-forge cxx-compiler setuptools setuptools-scm cython pythran pytest
    pip install -e . --no-build-isolation

    # (Optional) Test your installation
    cd test; pytest

