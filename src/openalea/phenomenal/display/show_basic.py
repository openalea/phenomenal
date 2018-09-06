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

from .Scene import Scene
# ==============================================================================


def show_mesh(vertices, faces, color=(0.1, 0.8, 0.1), colors=None):

    scene = Scene()
    actor = scene.get_actor_from_vertices_faces(vertices,
                                                faces,
                                                color=color,
                                                colors=colors)
    scene.add_actor(actor)
    scene.show()


def show_voxel_grid(voxel_grid,
                    color=(0.1, 0.8, 0.1),
                    windows_size=(600, 800),
                    screenshot_filename=None,
                    screenshot_magnification=10,
                    record_filename=None,
                    record_quality=2,
                    record_rate=100):

    scene = Scene()
    actor = scene.get_actor_from_voxels(
        voxel_grid.voxels_position,
        voxel_grid.voxels_size,
        color=color)
    scene.add_actor(actor)
    scene.show(windows_size=windows_size,
               screenshot_filename=screenshot_filename,
               screenshot_magnification=screenshot_magnification,
               record_filename=record_filename,
               record_quality=record_quality,
               record_rate=record_rate)


def show_vtk_poly_data(vtk_poly_data, color=(0, 1, 0)):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(vtk_poly_data)

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


# ==============================================================================


def record_voxel_grids(voxel_grids, filename, color=(0, 0.8, 0)):

    scene = Scene()

    def func(voxel_grid):
        scene.add_actor_from_voxels(voxel_grid.voxels_position,
                                    voxel_grid.voxels_size,
                                    color=color)

    scene.set_camera(elevation=20)
    scene.record_video(filename, voxel_grids, func)
