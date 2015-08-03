# -*- python -*-
#
#       tools_test: Module Description
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 
from mayavi import mlab
import cv2

import matplotlib.pyplot as plt
import numpy as np

from numpy import *
import pylab as p
import mpl_toolkits.mplot3d.axes3d as p3

import vtk
from numpy import *

#       =======================================================================
#       Local Import 


#       =======================================================================
#       Code

def load_images(images_path, angles):

    images = dict()
    i = 0

    for i in range(len(images_path)):
        im = cv2.imread(images_path[i], cv2.CV_LOAD_IMAGE_GRAYSCALE)
        images[angles[i]] = im

    return images


def show_cube(cubes, scale_factor, name=None):
    xx = []
    yy = []
    zz = []
    ss = []
    for cube in cubes:
        xx.append(int(round(cube.center.x)))
        yy.append(int(round(cube.center.y)))
        zz.append(int(round(cube.center.z)))
        ss.append(int(round(cube.radius)))

    if name is not None:
        mlab.figure(name)
    else:
        mlab.figure("3D Reconstruction")
    mlab.points3d(xx, yy, zz, mode='cube',
                  color=(0.1, 0.7, 0.1),
                  scale_factor=scale_factor)
    mlab.show()


def write_images_on_matrix(images, m):
    img = images[1]
    h, l = np.shape(img)
    xl, yl, zl = np.shape(m)
    resized_image = cv2.resize(img, (xl, zl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255
    for h in range(zl):
        for l in range(xl):
            if resized_image[h, l] == 255:
                m[l, 0, zl - 30 - h - 1] = 100
            else:
                m[l, 0, zl - 30 - h - 1] = 70

    # ======================================================================

    img = images[2]
    h, l = np.shape(img)
    xl, yl, zl = np.shape(m)
    resized_image = cv2.resize(img, (xl, zl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255
    for h in range(zl):
        for l in range(xl):
            if resized_image[h, l] == 255:
                m[0, l, zl - 30 - h - 1] = 100
            else:
                m[0, l, zl - 30 - h - 1] = 70

    # ======================================================================

    img = images[0]
    h, l = np.shape(img)
    print h, l

    xl, yl, zl = np.shape(m)
    print xl, yl, zl

    resized_image = cv2.resize(img, (xl, yl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255

    print np.shape(resized_image)
    for h in range(xl):
        for l in range(yl):
            if resized_image[h, l] == 255:
                m[l, yl - h - 1, zl - 1] = 100
            else:
                m[l, yl - h - 1, zl - 1] = 70
    return m


def create_matrix(height, length):
    matrix = np.zeros([length,
                       length,
                       height], dtype=np.uint8)

    return matrix


def fill_matrix(cubes, m):
    while True:
        try:
            cube = cubes.popleft()

            r = cube.radius / 10.0
            x = cube.center.x / 10.0
            y = cube.center.y / 10.0
            z = cube.center.z / 10.0

            m[x - r:x + r,
              y - r:y + r,
              z - r:z + r] = 50

        except IndexError:
            break

    return m


def show_mat(cubes):

    xx = []
    yy = []
    zz = []
    ss = []
    for cube in cubes:
        xx.append(int(round(cube.center.x)))
        yy.append(int(round(cube.center.y)))
        zz.append(int(round(cube.center.z)))
        ss.append(int(round(cube.radius)))

    fig = p.figure()
    ax = p3.Axes3D(fig)
    ax.scatter3D(xx, yy, zz)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    p.show()


def show_mat_2(cubes):

    xx = []
    yy = []
    zz = []
    ss = []
    for cube in cubes:
        xx.append(int(round(cube.center.x)))
        yy.append(int(round(cube.center.y)))
        zz.append(int(round(cube.center.z)))
        ss.append(int(round(cube.radius)))

    print len(xx), len(yy), len(zz)

    x, y, z = np.meshgrid(xx, yy, zz)

    print np.shape(x), np.shape(y), np.shape(z)

    mlab.figure()
    mlab.points3d(xx, yy, zz)


def show_mat_vtk(data_matrix):
    # # We begin by creating the data we want to render.
    # # For this tutorial, we create a 3D-image containing three overlaping cubes.
    # # This data can of course easily be replaced by data from a medical CT-scan or anything else three dimensional.
    # # The only limit is that the data must be reduced to unsigned 8 bit or 16 bit integers.
    # data_matrix = zeros([75, 75, 75], dtype=uint8)
    # data_matrix[0:35, 0:35, 0:35] = 50
    # data_matrix[25:55, 25:55, 25:55] = 100
    # data_matrix[45:74, 45:74, 45:74] = 150

    lx, ly, lz = np.shape(data_matrix)

    # For VTK to be able to use the data, it must be stored as a VTK-image.
    # This can be done by the vtkImageImport-class which imports raw data
    # and stores it.
    dataImporter = vtk.vtkImageImport()

    # The preaviusly created array is converted to a string of chars and
    # imported.
    data_string = data_matrix.tostring()
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))
    # The type of the newly imported data is set to unsigned char (uint8)
    dataImporter.SetDataScalarTypeToUnsignedChar()
    # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer
    # must be told this is the case.
    dataImporter.SetNumberOfScalarComponents(1)
    # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
    # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
    # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
    # VTK complains if not both are used.
    dataImporter.SetDataExtent(0, lx - 1, 0, ly - 1, 0, lz - 1)
    dataImporter.SetWholeExtent(0, lx - 1, 0, ly - 1, 0, lz - 1)

    # The following class is used to store transparencyv-values for later retrival. In our case, we want the value 0 to be
    # completly opaque whereas the three different cubes are given different transperancy-values to show how it works.
    alphaChannelFunc = vtk.vtkPiecewiseFunction()
    alphaChannelFunc.AddPoint(0, 0.001)
    alphaChannelFunc.AddPoint(50, 1.0)
    alphaChannelFunc.AddPoint(100, 0.1)
    alphaChannelFunc.AddPoint(150, 0.2)

    # This class stores color data and can create color tables from a few color points. For this demo, we want the three cubes
    # to be of the colors red green and blue.
    colorFunc = vtk.vtkColorTransferFunction()

    # colorFunc.AddRGBPoint(0, 0.0, 0.0, 0.0)
    colorFunc.AddRGBPoint(50, 1.0, 0.0, 0.0)
    colorFunc.AddRGBPoint(100, 0.0, 1.0, 0.0)
    colorFunc.AddRGBPoint(150, 0.0, 0.0, 1.0)

    # The preavius two classes stored properties. Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(alphaChannelFunc)

    # This class describes how the volume is rendered (through ray tracing).
    compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    # We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkVolumeRayCastMapper()
    volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

    # The class vtkVolume is used to pair the preaviusly declared volume as well as the properties to be used when rendering that volume.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    # With almost everything else ready, its time to initialize the renderer and window, as well as creating a method for exiting the application
    renderer = vtk.vtkRenderer()
    renderWin = vtk.vtkRenderWindow()
    renderWin.AddRenderer(renderer)
    renderInteractor = vtk.vtkRenderWindowInteractor()
    renderInteractor.SetRenderWindow(renderWin)

    # We add the volume to the renderer ...
    renderer.AddVolume(volume)
    # ... set background color to white ...
    renderer.SetBackground(0, 0, 0)
    # ... and set window size.
    renderWin.SetSize(400, 400)

    # A simple function to be called when the user decides to quit the application.
    def exitCheck(obj, event):
        if obj.GetEventPending() != 0:
            obj.SetAbortRender(1)

    # Tell the application to use the function as an exit check.
    renderWin.AddObserver("AbortCheckEvent", exitCheck)

    renderInteractor.Initialize()
    # Because nothing will be rendered without any input, we order the first render manually before control is handed over to the main-loop.
    renderWin.Render()
    renderInteractor.Start()

    cv2.waitKey()
