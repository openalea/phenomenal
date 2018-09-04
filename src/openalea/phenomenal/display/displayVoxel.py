# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function

import vtk
import random
import numpy.random


from .display import Display
# ==============================================================================


class DisplayVoxel(Display):

    def __init__(self):
        Display.__init__(self)

    def add_actor(self, actor):
        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actors(self, actors):
        for actor in actors:
            self.add_actor(actor)

    def add_actor_from_plane(self,
                             center,
                             normal,
                             color=(0, 0, 1),
                             radius=100):

        source = vtk.vtkPlaneSource()
        source.SetXResolution(radius)
        source.SetYResolution(radius)

        d = - (normal[0] * center[0] +
               normal[1] * center[1] +
               normal[2] * center[2])

        origin = (center[0] - 50, center[1] - radius / 2)
        z = (- normal[0] * origin[0] - normal[1] * origin[1] - d) / normal[2]
        source.SetOrigin(origin[0], origin[1], z)

        p1 = (origin[0] + radius, origin[1])
        z = (- normal[0] * p1[0] - normal[1] * p1[1] - d) / normal[2]
        source.SetPoint1(p1[0], p1[1], z)

        p1 = (origin[0], origin[1] + radius)
        z = (- normal[0] * p1[0] - normal[1] * p1[1] - d) / normal[2]
        source.SetPoint2(p1[0], p1[1], z)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])

        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actor_from_text(self,
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

        self._text_actors.append(actor)
        self._renderer.AddActor(actor)

        return actor

    def add_actor_from_ball_position(self,
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

        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actor_from_arrow_vector(self,
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

        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actor_from_vertices_faces(self,
                                      vertices,
                                      faces,
                                      colors=None,
                                      color=None,):

        # if color is None:
        #     color = numpy.random.uniform(0, 1, 3)

        # Setup the colors array
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName("Colors")

        # ======================================================================

        def make_vtk_id_list(it):
            vil = vtk.vtkIdList()
            for j in it:
                vil.InsertNextId(int(j))
            return vil

        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()

        # Load the point, cell, and data attributes.
        for i in range(len(vertices)):
            points.InsertPoint(i, vertices[i])
        poly_data.SetPoints(points)
        del points

        for i in range(len(faces)):
            polys.InsertNextCell(make_vtk_id_list(faces[i]))
        poly_data.SetPolys(polys)
        del polys

        if colors is not None:
            vtk_colors = vtk.vtkUnsignedCharArray()
            vtk_colors.SetNumberOfComponents(3)
            vtk_colors.SetName("Colors")
            for color in colors:
                vtk_colors.InsertNextTuple3(color[0], color[1], color[2])
            poly_data.GetCellData().SetScalars(vtk_colors)

        # ======================================================================

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if color is not None and colors is None:
            actor.GetProperty().SetColor(color[0], color[1], color[2])

        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actor_from_voxels(self,
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

        self._actors.append(actor)
        self._renderer.AddActor(actor)

    def add_actors_from_voxels_list(self,
                                    voxels_positions,
                                    voxels_sizes,
                                    colors=None):

        if colors is None:
            colors = [None] * len(voxels_sizes)

        for voxels_position, voxels_size, color in zip(
                voxels_positions, voxels_sizes, colors):
            self.add_actor_from_voxels(voxels_position,
                                       voxels_size,
                                       color=color)
