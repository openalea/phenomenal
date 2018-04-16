# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""

"""
# ==============================================================================
from __future__ import division, print_function

import vtk
# ==============================================================================

__all__ = ["show_poly_data"]

# ==============================================================================


def show_poly_data(poly_data, colored=True):

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)

    if colored:
        nb = poly_data.GetNumberOfPoints()
        scalars = vtk.vtkFloatArray()
        for i in range(nb):
            scalars.InsertTuple1(i, i)
        poly_data.GetPointData().SetScalars(scalars)
        mapper.SetScalarRange(0, nb - 1)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # The usual rendering stuff.
    camera = vtk.vtkCamera()
    camera.SetPosition(1, 1, 1)
    camera.SetFocalPoint(0, 0, 0)

    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    renderer.AddActor(actor)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.SetBackground(0, 0, 0)
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
