#!/usr/bin/env bash

# ==============================================================================
# Install system

sudo apt-get update
sudo apt-get -y install git
sudo apt-get -y install freeglut3-dev

chmod 600 gitlab_private_key
echo "export GIT_SSH_COMMAND=\"ssh -i ./gitlab_private_key\"" >> ~/.bashrc
export GIT_SSH_COMMAND="ssh -i ./gitlab_private_key"

# ==============================================================================
#                           Local Installation
# ==============================================================================

# CONDA Installation

wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
chmod +x  miniconda.sh

bash miniconda.sh -b -p $HOME/miniconda
echo "# added by Miniconda2 4.3.11 installer" >> ~/.bashrc
echo "export PATH=\"~/miniconda/bin:\$PATH\"" >> ~/.bashrc
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install conda-build

# CONDA create and activate virtual environement
conda create --name phenome python
source activate phenome

# Install phenomenal
git clone git@gitlab.inria.fr:sartzet/phenomenal.git
cd ./phenomenal/build_tools/conda
conda build -c conda-forge -c openalea .
conda install -c conda-forge -c openalea --use-local openalea.phenomenal
cd ../../../

# Install phenoarch
git clone git@gitlab.inria.fr:sartzet/phenoarch.git
cd ./phenoarch/
conda install -c conda-forge -c openalea pymongo pandas
python setup.py develop
cd ..

# python-irodsclient
git clone https://github.com/irods/python-irodsclient
cd ./python-irodsclient/
python setup.py develop