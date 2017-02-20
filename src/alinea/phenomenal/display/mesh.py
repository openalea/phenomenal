# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
"""

"""
# ==============================================================================
import vtk
import mayavi.mlab

from alinea.phenomenal.display.center_axis import plot_center_axis
# ==============================================================================

__all__ = ["show_mesh", "show_poly_data"]

# ==============================================================================


def show_mesh(vertices, faces,
              normals=None,
              centers=None,
              color=None,
              representation='surface',
              figure_name="",
              size=(800, 700),
              with_center_axis=False,
              azimuth=None,
              elevation=None,
              distance=None,
              focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    if normals is not None and centers is not None:
        mayavi.mlab.quiver3d(centers[:, 0], centers[:, 1], centers[:, 2],
                             normals[:, 0], normals[:, 1], normals[:, 2],
                             line_width=1.0, scale_factor=1)

    mayavi.mlab.triangular_mesh([vert[0] for vert in vertices],
                                [vert[1] for vert in vertices],
                                [vert[2] for vert in vertices],
                                faces,
                                color=color,
                                representation=representation)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


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