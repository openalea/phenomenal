============================
Installation on Cloud Ubuntu
============================

.. contents::

hostnanme
---------

cat /etc/host
nano /etC/hostname


Install Machines
----------------

.. code:: shell

    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install freeglut3-dev

Download an Install Conda
-------------------------

See : http://conda.pydata.org/miniconda.html

.. code:: shell

    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
    chmod +x  Miniconda2-latest-Linux-x86_64.sh
    ./Miniconda2-latest-Linux-x86_64.sh


Create virtual environment
..........................

.. code:: shell

    conda create --name phenome python
    source activate phenome


Install Requirements:
.....................

.. code:: shell

conda install jupyter nose opencv scipy networkx vtk matplotlib scikit-learn
conda install -c openalea openalea.deploy openalea.core openalea.grapheditor

Install Phenomenal
..................

.. code:: shell

    git clone https://gitlab.inria.fr/phenome/phenomenal.git
    cd phenomenal
    python setup.py develop --prefix=$CONDA_PREFIX
    cd ..

Install Phenoarch
.................

.. code:: shell

    conda install pymongo pandas

    git clone https://artzet_s@scm.gforge.inria.fr/authscm/artzet_s/git/phenoarch/phenoarch.git
    cd phenoarch
    python setup.py develop --prefix=$CONDA_PREFIX
    cd ..

Install PythreeJs
.................

.. code:: shell
    sudo apt-get install npm nodejs-legacy

    git clone https://github.com/avmarchenko/pythreejs
    cd pythreejs
    python setup.py develop --prefix=$CONDA_PREFIX
    jupyter nbextension install --py --symlink --sys-prefix pythreejs
    jupyter nbextension enable --py --sys-prefix pythreejs

Launch Notebook Server
......................

.. code:: shell

    pscp.exe -i FG_Cloud_Strasbourg_Pricate_key_Simon.ppk linux-openvpn-users.zip ubuntu@134.158.151.25:.

    sudo apt-get install unzip openvpn resolvconf

    sudo openvpn --config openvpn-udp-1193-vpn_users.ovpn &
    disown




    disown


