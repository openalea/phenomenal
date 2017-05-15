#!/bin/bash

cd ~

# ==============================================================================
# Install system

sudo apt-get update
sudo apt-get -y install git
sudo apt-get -y install freeglut3-dev

# ==============================================================================
# Configuration

echo "-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----" > gitlab_private_key

chmod 600 gitlab_private_key
echo "export GIT_SSH_COMMAND=\"ssh -i ~/gitlab_private_key\"" >> ~/.bashrc
export GIT_SSH_COMMAND="ssh -i ~/gitlab_private_key"

# ==============================================================================
# Download

git clone git@gitlab.inria.fr:phenome/phenomenal.git
git clone git@gitlab.inria.fr:phenome/phenoarch.git
git clone https://github.com/irods/python-irodsclient
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh

# ==============================================================================
# Git Branch version

cd phenomenal
git checkout develop
git pull
cd ..

cd phenoarch
git checkout feature/deploy_cloud
git pull
cd ..

# ==============================================================================
#                           Local Installation
# ==============================================================================

# CONDA Installation
chmod +x  Miniconda2-latest-Linux-x86_64.sh
./Miniconda2-latest-Linux-x86_64.sh -b

echo "# added by Miniconda2 4.3.11 installer" >> ~/.bashrc
echo "export PATH=\"/home/ubuntu/miniconda2/bin:\$PATH\"" >> ~/.bashrc
export PATH="/home/ubuntu/miniconda2/bin:$PATH"

# CONDA create and activate virtual environement

conda create --name phenome --file ~/phenomenal/install/dependency-cloud-ubuntu.txt
source activate phenome

# Install phenomenal
cd ~/phenomenal/
python setup.py develop --prefix=$CONDA_PREFIX
cd ~

# Install phenoarch
cd ~/phenoarch/
python setup.py develop --prefix=$CONDA_PREFIX
cd ~

# python-irodsclient
cd ~/python-irodsclient/
python setup.py develop --prefix=$CONDA_PREFIX
cd ~