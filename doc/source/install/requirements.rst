============
Requirements
============

.. contents::

--------------------------------------------------------------------------------

Setuptools
----------

- Link :
    - https://pypi.python.org/pypi/setuptools
    - https://pythonhosted.org/setuptools/

- Short description :
    Setuptools is a fully-featured, actively-maintained,
    and stable library designed to facilitate packaging Python projects,
    where packaging includes:

    - Python package and module definitions
    - Distribution package metadata
    - Test hooks
    - Project installation
    - Platform-specific details
    - Python 3 support

- Utility in Phenomenal :
    Setuptools is used so setting up setup.py


Numpy
-----

- Link :
    - http://www.numpy.org/

- Short description :
    NumPy is the fundamental package for scientific computing in Python.
    It is a Python library that provides a multidimensional array object,
    various derived objects (such as masked arrays and matrices),
    and an assortment of routines for fast operations on arrays,
    including mathematical, logical, shape manipulation, sorting, selecting,
    I/O, discrete Fourier transforms, basic linear algebra, basic statistical
    operations, random simulation and much more.

- Utility in Phenomenal :
    Numpy is used to manipulate matrix and array

--------------------------------------------------------------------------------

Matplotlib
----------

- Link :
    - http://matplotlib.org/

- Short description :
    matplotlib is a python 2D plotting library which produces publication
    quality figures in a variety of hardcopy formats and interactive
    environments across platforms. matplotlib can be used in python scripts,
    the python and ipython shell (ala MATLAB®* or Mathematica®†),
    web application servers, and six graphical user interface toolkits

- Utility in Phenomenal :
    Matplotlib is used to display image RGB and binarized

--------------------------------------------------------------------------------

Scipy
-----

- Link :
    - http://www.scipy.org/

- Short description :
    SciPy is a collection of mathematical algorithms and convenience
    functions built on the Numpy extension of Python. It adds significant
    power to the interactive Python session by providing the user with
    high-level commands and classes for manipulating and visualizing data.
    With SciPy an interactive Python session becomes a data-processing and
    system-prototyping environment rivaling systems such as MATLAB, IDL,
    Octave, R-Lab, and SciLab

- Utility in Phenomenal :
    To minimize objective function in calibration process

--------------------------------------------------------------------------------

Scikit-Image
------------

- Link :
    - http://scikit-image.org/

- Short description :
    The scikit-image SciKit (toolkit for SciPy) extends scipy.ndimage to provide
    a versatile set of image processing routines.
    It is written in the Python language.

- Utility in Phenomenal :
    To skeletonize 2D image

--------------------------------------------------------------------------------

OpenCV (Open Source Computer Vision)
------------------------------------

- Link :
    - http://opencv.org/

- Short description :
    OpenCV (Open Source Computer Vision) is a library that includes
    several hundreds of computer vision algorithms.

    The library is cross-platform and free for use under the open-source BSD
    license.

- Utility in Phenomenal :
    - Load image
    - Detect Chessboard in 2D image

--------------------------------------------------------------------------------

VTK (The Visualization Toolkit)
-------------------------------

- Link :
    http://www.vtk.org/

- Short description :
    The Visualization Toolkit (VTK) is an open-source, freely available software
    system for 3D computer graphics, image processing and visualization.
    VTK consists of a C++ class library and several interpreted interface layers
    including Tcl/Tk, Java, and Python

- Utility in Phenomenal :
    - Visualize 3D object (Requirement of mayavi)
    - Produce mesh from image 3D (Marching cube, mesh decimation)

--------------------------------------------------------------------------------

IPython & IPython-notebook
--------------------------

- Link :
    - http://ipython.org/
    - http://ipython.org/notebook.html

- Short description :
    The IPython Notebook is an interactive computational environment,
    in which you can combine code execution, rich text, mathematics,
    plots and rich media

- Utility in Phenomenal :
    - Replay ipython-notebook benchmarks

--------------------------------------------------------------------------------

Nose
----

- Link :
    - https://nose.readthedocs.org/en/latest/

- Short description :
    Nose extends unittest to make testing easier

- Utility in Phenomenal :
    - Launch and manage unit-test

--------------------------------------------------------------------------------

OpenAlea
--------

- Link :
    - http://openalea.gforge.inria.fr/dokuwiki/doku.php

- Short Description :

    OpenAlea is an open source project primarily aimed at the plant research
    community. It is a distributed collaborative effort to develop Python
    libraries and tools that address the needs of current and future works in
    Plant Architecture modeling. OpenAlea includes modules to analyse,
    visualize and model the functioning and growth of plant architecture.

- Utility in Phenomenal :
    - Plugin interface utilization

--------------------------------------------------------------------------------

OpenAlea.Deploy
'''''''''''''''

- https://github.com/openalea/deploy

OpenAlea.Deploy support the installation of OpenAlea packages via the network
and manage their dependencies . It is an extension of Setuptools.

- Requirements :
    - Python <= 2.7
    - Setuptools

--------------------------------------------------------------------------------

OpenAlea.SConsX
'''''''''''''''

- https://github.com/openalea/sconsx

SConsX is an extension package of the famous SCons build tool. SConsX aims
to simplify the build of complex multi-platform packages
(i.e. using C++, Boost.Python and Python).

- Requirements :
    - SCons (http://www.scons.org) version >= 0.96.93
    - deploy (https://github.com/openalea/deploy)

--------------------------------------------------------------------------------

OpenAlea.OpenAlea
'''''''''''''''''

- https://github.com/openalea/openalea

SConsX is an extension package of the famous SCons build tool. SConsX aims
to simplify the build of complex multi-platform packages
(i.e. using C++, Boost.Python and Python).

- Requirements :
    - deploy (https://github.com/openalea/deploy)
    - sconsx (https://github.com/openalea/sconsx)
    - PyQt4 (https://riverbankcomputing.com/software/pyqt/intro)
    - ipython (http://ipython.org/)

--------------------------------------------------------------------------------

OpenAlea.OpenAlea-Components
''''''''''''''''''''''''''''

- https://github.com/openalea/openalea-components

- Requirements :
    - openalea (https://github.com/openalea/openalea)
