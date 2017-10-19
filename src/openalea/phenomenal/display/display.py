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
# ==============================================================================


class Display(object):

    def __init__(self,
                 background_color=(1, 1, 1)):

        self._actors = list()
        self._camera = vtk.vtkCamera()
        self._renderer = vtk.vtkRenderer()
        self._renderer.SetActiveCamera(self._camera)

        self.set_camera(elevation=-90, azimuth=-90)
        self.set_background_color(background_color)

    def set_camera(self,
                   elevation=0,
                   azimuth=0,
                   position=None,
                   focal_point=None,
                   distance=None):

        self._camera.Elevation(elevation)
        self._camera.OrthogonalizeViewUp()
        self._camera.Azimuth(azimuth)
        if position:
            self._camera.SetPosition(position[0],
                                     position[1],
                                     position[2])
        if focal_point:
            self._camera.SetFocalPoint(focal_point[0],
                                       focal_point[1],
                                       focal_point[2])
        if distance:
            self._camera.SetDistance(distance)

    def reset_camera(self):
        self._renderer.ResetCamera()

    def add_actors(self,
                   actors):

        for actor in actors:
            self._actors.append(actor)
            self._renderer.AddActor(actor)

    def clean_all_actors(self):

        for actor in self._actors:
            self._renderer.RemoveActor(actor)

    def set_background_color(self,
                             color):

        self._renderer.SetBackground(color[0], color[1], color[2])

    def export_scene_to_x3d(self,
                            file_prefix):

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(self.renderer)

        exporter = vtk.vtkX3DExporter()
        exporter.SetInput(render_window)
        exporter.SetFileName(file_prefix + '.x3d')
        exporter.Write()

        del render_window

    def export_scene_to_vrml(self,
                             file_prefix):

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(self.renderer)

        exporter = vtk.vtkVRMLExporter()
        exporter.SetInput(render_window)
        exporter.SetFileName(file_prefix + '.wrl')
        exporter.Write()

        del render_window

    def screenshot(self,
                   filename,
                   magnification=10):

        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)
        render_window.AddRenderer(self._renderer)
        render_window.Render()

        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(render_window)
        window_to_image_filter.SetMagnification(magnification)
        window_to_image_filter.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(filename)
        writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        writer.Write()

        del render_window

    def show(self,
             windows_size=(600, 800)):

        self.reset_camera()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(self._renderer)
        render_window.SetSize(windows_size[0], windows_size[1])

        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())
        render_window_interactor.SetRenderWindow(render_window)

        render_window.Render()
        render_window_interactor.Start()

        del render_window
        del render_window_interactor


