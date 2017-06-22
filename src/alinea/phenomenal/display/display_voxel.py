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

# ==============================================================================


class DisplayVoxel(object):

    def __init__(self):
        pass

    def vtk_save_actors_scene_to_x3d(self, actors, file_prefix):

        renderer = vtk.vtkRenderer()
        for actor in actors:
            renderer.AddActor(actor)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        exporter = vtk.vtkX3DExporter()
        exporter.SetInput(render_window)
        exporter.SetFileName(file_prefix + '.x3d')
        exporter.Write()

    def vtk_save_actors_scene_to_vrml(self, actors, file_prefix):

        renderer = vtk.vtkRenderer()
        for actor in actors:
            renderer.AddActor(actor)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        exporter = vtk.vtkVRMLExporter()
        exporter.SetInput(render_window)
        exporter.SetFileName(file_prefix + '.wrl')
        exporter.Write()

    def vtk_get_text_actor(self,
                           text,
                           position=(0, 0, 0),
                           scale=5,
                           color=(0, 0, 1)):

        textSource = vtk.vtkVectorText()
        textSource.SetText(text)
        textSource.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(textSource.GetOutputPort())

        actor = vtk.vtkFollower()
        actor.SetMapper(mapper)
        actor.SetScale(scale, scale, scale)
        actor.AddPosition(position[0], position[1], position[2])

        actor.GetProperty().SetColor(color[0], color[1], color[2])

        return actor

    def vtk_get_ball_actor_from_position(self,
                                         position,
                                         radius=5,
                                         color=(1, 0, 0)):

        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(position[0], position[1], position[2])
        sphereSource.SetRadius(radius)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])

        return actor

    def vtk_get_arrow_vector(self,
                             startPoint,
                             endPoint,
                             color=(0, 0, 0),
                             line_width=20):

        arrowSource = vtk.vtkArrowSource()

        random.seed(8775070)

        # Compute a basis
        normalizedX = [0] * 3
        normalizedY = [0] * 3
        normalizedZ = [0] * 3
        # The X axis is a vector from start to end

        math = vtk.vtkMath()
        math.Subtract(endPoint, startPoint, normalizedX)
        length = math.Norm(normalizedX)
        math.Normalize(normalizedX)

        # The Z axis is an arbitrary vector cross X
        arbitrary = [0] * 3
        arbitrary[0] = random.uniform(-10, 10)
        arbitrary[1] = random.uniform(-10, 10)
        arbitrary[2] = random.uniform(-10, 10)
        math.Cross(normalizedX, arbitrary, normalizedZ)
        math.Normalize(normalizedZ)

        # The Y axis is Z cross X
        math.Cross(normalizedZ, normalizedX, normalizedY)
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
            matrix.SetElement(i, 0, normalizedX[i])
            matrix.SetElement(i, 1, normalizedY[i])
            matrix.SetElement(i, 2, normalizedZ[i])

        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(startPoint)
        transform.Concatenate(matrix)
        transform.Scale(length, line_width, line_width)

        # Transform the polydata
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(arrowSource.GetOutputPort())

        # Create a mapper and actor for the arrow
        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()

        mapper.SetInputConnection(transformPD.GetOutputPort())
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])

        return actor

    def vtk_get_actor_from_voxels(self,
                                  voxels_position,
                                  voxels_size,
                                  color=None):
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

    def vtk_show_actor(self, actors):
        # The usual rendering stuff.
        camera = vtk.vtkCamera()
        # camera.SetPosition(1, 1, 1)
        # camera.SetFocalPoint(0, 0, 0)

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
        # del camera
        del renderer
        del render_window
        # del render_window_interactor


    def show(self, voxel_segmentation, color=None):
        raise NotImplementedError