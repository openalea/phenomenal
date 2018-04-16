# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import vtk
# ==============================================================================


def vtk_voxel_point_cloud_to_polydata(vpc, color=None):
    voxels_position = vpc.voxels_position
    voxels_size = vpc.voxels_size

    points = vtk.vtkPoints()
    for v in voxels_position:
        points.InsertNextPoint(v[0], v[1], v[2])

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    cubeSource = vtk.vtkCubeSource()
    cubeSource.SetXLength(voxels_size)
    cubeSource.SetYLength(voxels_size)
    cubeSource.SetZLength(voxels_size)

    glyph3D = vtk.vtkGlyph3D()

    if vtk.VTK_MAJOR_VERSION <= 5:
        glyph3D.SetSource(cubeSource.GetOutput())
        glyph3D.SetInput(polydata)
    else:
        glyph3D.SetSourceConnection(cubeSource.GetOutputPort())
        glyph3D.SetInputData(polydata)

    glyph3D.Update()

    return glyph3D.GetOutput()


def vtk_show_poly_data(poly_data, color=(0, 1, 0)):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)

    # if colored:
    #     nb = poly_data.GetNumberOfPoints()
    #     scalars = vtk.vtkFloatArray()
    #     for i in range(nb):
    #         scalars.InsertTuple1(i, i)
    #     poly_data.GetPointData().SetScalars(scalars)
    #     mapper.SetScalarRange(0, nb - 1)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])

    # The usual rendering stuff.
    camera = vtk.vtkCamera()
    camera.SetPosition(1, 1, 1)
    camera.SetFocalPoint(0, 0, 0)

    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetInteractorStyle(
        vtk.vtkInteractorStyleTrackballCamera())
    render_window_interactor.SetRenderWindow(render_window)

    renderer.AddActor(actor)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.SetBackground(0.5, 0.5, 0.5)
    render_window.SetSize(600, 600)

    # interact with data
    render_window.Render()
    render_window_interactor.Start()

    # Clean up
    del mapper
    del actor
    del camera
    del renderer
    del render_window
    del render_window_interactor
