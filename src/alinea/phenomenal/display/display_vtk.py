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

import vtk
import random

def vtk_show_voxel_points_cloud(voxel_points_cloud,
                                color=(0, 1, 0)):

    actor = vtk_get_actor_from_voxels(voxel_points_cloud.voxels_position,
                                      voxel_points_cloud.voxels_size,
                                      color=color)

    vtk_show_actor([actor])


def vtk_show_actor(actors):

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

    for actor in actors:
        renderer.AddActor(actor)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.SetBackground(0.4, 0.4, 0.4)
    render_window.SetSize(600, 600)

    # interact with data
    render_window.Render()
    render_window_interactor.Start()

    # Clean up
    for actor in actors:
        del actor
    del camera
    del renderer
    del render_window
    del render_window_interactor


def vtk_show_voxel_skeleton(voxel_skeleton):

    actors = list()

    for vs in voxel_skeleton.voxel_segments:
        actor_voxels = vtk_get_actor_from_voxels(
            vs.voxels_position,
            voxel_skeleton.voxels_size * 0.25)

        actors.append(actor_voxels)

        actor_polyline = vtk_get_actor_from_voxels(
            vs.polyline, voxel_skeleton.voxels_size, color=(0, 0, 0))

        actors.append(actor_polyline)

    vtk_show_actor(actors)


def vtk_show_voxel_maize_segmentation(voxel_maize_segmentation):

    vms = voxel_maize_segmentation

    actors = list()

    color = {"stem": (0, 0, 0),
             "mature_leaf": None,
             "cornet_leaf": (1, 0, 0),
             "unknown": (1, 1, 1)}

    for vo in vms.voxel_organs:

        actor_voxels = vtk_get_actor_from_voxels(
            vo.voxels_position(),
            vms.voxels_size * 0.50,
            color=color[vo.label])

        actors.append(actor_voxels)

        for vs in vo.voxel_segments:
            actor_polyline = vtk_get_actor_from_voxels(
                vs.polyline,
                vms.voxels_size * 0.50,
                color=(1, 1, 1))

            actors.append(actor_polyline)

    vtk_show_actor(actors)


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


def vtk_get_actor_from_voxels(voxels_position, voxels_size, color=None):

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

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

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])

    return actor


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

