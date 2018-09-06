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

import time
import vtk
import math
import numpy
from threading import Lock

from ..calibration.transformations import rotation_matrix

# ==============================================================================


class Display(object):

    def __init__(self,
                 background_color=(1, 1, 1)):

        self._actors = list()
        self._text_actors = list()
        self._camera = vtk.vtkCamera()
        self._renderer = vtk.vtkRenderer()
        self._renderer.SetActiveCamera(self._camera)

        self.set_camera(elevation=-90, azimuth=-90)
        self.set_background_color(background_color)

        self._R = rotation_matrix(math.pi / 180.0, [0, 0, 1], [0, 0, 0])

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

    def clean_all_actors(self):

        for actor in self._actors + self._text_actors:
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

    def render(self, windows_size=(600, 800)):

        self.reset_camera()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(self._renderer)
        render_window.SetSize(windows_size[0], windows_size[1])
        render_window.Render()

    def show(self,
             windows_size=(600, 800),
             screenshot_filename=None,
             screenshot_magnification=10,
             record_filename=None,
             record_quality=2,
             record_rate=25):

        self.reset_camera()

        if record_filename is not None:
            self.init_record_video(record_filename,
                                   windows_size=windows_size,
                                   quality=record_quality,
                                   rate=record_rate)
        else:
            self.render_window = vtk.vtkRenderWindow()
            self.render_window.AddRenderer(self._renderer)
            self.render_window.SetSize(windows_size[0], windows_size[1])

            self.render_window_interactor = vtk.vtkRenderWindowInteractor()
            self.render_window_interactor.SetInteractorStyle(
                vtk.vtkInteractorStyleTrackballCamera())
            self.render_window_interactor.SetRenderWindow(self.render_window)
            self.render_window.Render()

        if record_filename is not None:
            self.stop = False

        self.render_window_interactor.Start()

        if record_filename is not None:
            self.stop = True
            self.writer.End()

        del self.render_window
        del self.render_window_interactor

        if screenshot_filename is not None:
            self.screenshot(screenshot_filename,
                            magnification=screenshot_magnification)

    def init_record_video(self, filename,
                          windows_size=(800, 1000),
                          quality=2,
                          rate=25):

        self.stop = True
        self.reset_camera()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self._renderer)
        self.render_window.SetSize(windows_size[0], windows_size[1])

        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window_interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())
        self.render_window_interactor.SetRenderWindow(self.render_window)
        self.render_window.Render()

        self.windowToImageFilter = vtk.vtkWindowToImageFilter()
        self.windowToImageFilter.SetInput(self.render_window)
        self.windowToImageFilter.SetInputBufferTypeToRGB()
        self.windowToImageFilter.ReadFrontBufferOff()
        self.windowToImageFilter.Update()

        self.writer = vtk.vtkAVIWriter()
        self.writer.SetInputConnection(self.windowToImageFilter.GetOutputPort())
        self.writer.SetFileName(filename)
        self.writer.SetRate(rate)
        self.writer.SetQuality(quality)
        self.writer.Start()

        self.lock = Lock()
        def cb(interactor, event):
            if not self.stop and self.lock.acquire(False):
                self.windowToImageFilter.Modified()
                self.writer.Write()
                self.lock.release()

        self.render_window_interactor.AddObserver('TimerEvent', cb)
        self.render_window_interactor.AddObserver('RenderEvent', cb)
        self.render_window_interactor.CreateRepeatingTimer(1)

    def record_video(self, video_filename, elements, func):

        self.init_record_video(video_filename)

        if elements:
            element = elements[-1]
            func(element)
            self.reset_camera()
            self.clean_all_actors()

        self.switch_elements(elements, func)
        self.stop = False
        self.render_window_interactor.Start()

        del self.render_window
        del self.render_window_interactor

    def switch_elements(self, elements, func):
        self.it = 0
        def cb_change_plant(interactor, event):
            if not self.stop and self.lock.acquire(False):
                if self.it % 360 == 0:
                    if elements:
                        element = elements.pop(0)
                        self.clean_all_actors()
                        func(element)
                        self.it = 0
                    else:
                        self.writer.End()
                        self.clean_all_actors()
                        self.stop = True

                for actor in self._actors:
                    actor.RotateZ(1)

                for text_actor in self._text_actors:
                    x, y, z = text_actor.GetPosition()
                    pos = numpy.dot(self._R, numpy.array([x, y, z, 1]))
                    text_actor.SetPosition(pos[:3])
                    text_actor.SetCamera(self._renderer.GetActiveCamera())

                self.it += 1

                interactor.GetRenderWindow().Render()
                self.lock.release()

        self.render_window_interactor.AddObserver('TimerEvent', cb_change_plant)
        timerId = self.render_window_interactor.CreateRepeatingTimer(5)