=====================
Questions and Answers
=====================

.. contents::

How solve the server certificate verification failed problem on a ubuntu VM ?
-----------------------------------------------------------------------------

.. code:: shell

    export GIT_SSL_NO_VERIFY=1
    #or
    git config --global http.sslverify false

How solve the hostnanme on a ubuntu VM ?
----------------------------------------

    cat /etc/host
    nano /etc/hostname


How to install Python-Irodsclient ?
-----------------------------------

.. code:: shell

    git clone https://github.com/irods/python-irodsclient
    cd python-irodsclient; python setup.py install --prefix=$CONDA_PREFIX; cd ..

How launch a Notebook Server on a cloud VM ?
--------------------------------------------

.. code:: shell

    jupyter notebook --no-browser --ip=<local_ip> &
    disown
