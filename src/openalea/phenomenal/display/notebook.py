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
from pythreejs import (
    BufferGeometry,
    PointsMaterial,
    Points,
    Scene,
    DirectionalLight,
    PerspectiveCamera,
    OrbitControls,
    Renderer,
    AmbientLight)

import time
from IPython.display import display
from ipywidgets import HTML, Text
from traitlets import link, dlink
from itertools import chain


# ==============================================================================
class AnimateObjects(object):
    def __init__(self, objects):
        self.objects = objects

    def animate(self, time_visible_by_object=1.00):
        for i in range(len(self.objects)):
            self.set_index_objects_visible(i)
            time.sleep(time_visible_by_object)

    def set_index_objects_visible(self, index):
        for obj in self.objects:
            obj.visible = False
        self.objects[index].visible = True


def animate_voxel_point_cloud(list_voxel_point_cloud, t=1.00, size=("800", "600")):

    if not list_voxel_point_cloud:
        return None

    list_points = list()
    for voxel_point_cloud in list_voxel_point_cloud:

        voxel_center = voxel_point_cloud.voxels_center
        voxel_size = voxel_point_cloud.voxels_size

        # Transform to vertices display format
        vertices = list(chain.from_iterable(voxel_center))

        # Define points
        geometry = BufferGeometry(vertices=vertices)
        # Define colors and size points
        material = PointsMaterial(size=voxel_size, color='green')

        points = Points(geometry=geometry, material=material)

        list_points.append(points)

    children = list_points + [AmbientLight(color='#788777')]

    scene = Scene(children=children)

    children = DirectionalLight(color='white',
                                position=[0, 1000, 0],
                                intensity=0.4)

    camera = PerspectiveCamera(position=[-2000, 0, 0],
                               up=[0, 0, 1],
                               children=[children])

    # Define how far camera can view geometry in the scene
    camera.far = 8000

    controls = OrbitControls(controlling=camera)
    renderer = Renderer(camera=camera,
                        scene=scene,
                        controls=[controls])

    # Define size of window renderer
    renderer.width, renderer.height = size
    # Define background color and opacity of window renderer
    renderer.background_color = "black"
    renderer.background_opacity = 0.5

    ao = AnimateObjects(list_points)
    ao.set_index_objects_visible(0)

    # launch display
    display(renderer)

    ao.animate(time_visible_by_object=t)

    return ao


def show_voxel_point_cloud(voxel_point_cloud):

    voxel_center = voxel_point_cloud.voxels_center
    voxel_size = voxel_point_cloud.voxels_size

    # Transform to vertices display format
    vertices = list(chain.from_iterable(voxel_center))


def show_points(vertices, size,
                color_points='green',
                windows_size=("800", "600"),
                renderer_background_color="black",
                renderer_background_opacity=0.5):

    # Define points
    geometry = BufferGeometry(vertices=vertices)
    # Define colors and size points
    material = PointsMaterial(size=size, color=color_points)

    points = Points(geometry=geometry, material=material)

    scene = Scene(children=[points, AmbientLight(color='#788777')])

    children = DirectionalLight(color='white',
                                position=[0, 1000, 0],
                                intensity=0.4)

    camera = PerspectiveCamera(position=[-2000, 0, 0],
                               up=[0, 0, 1],
                               children=[children])

    # Define how far camera can view geometry in the scene
    camera.far = 8000

    controls = OrbitControls(controlling=camera)
    renderer = Renderer(camera=camera,
                        scene=scene,
                        controls=[controls])

    # Define size of window renderer
    renderer.width, renderer.height = windows_size
    # Define background color and opacity of window renderer
    renderer.background_color = renderer_background_color
    renderer.background_opacity = renderer_background_opacity

    # launch display
    display(renderer)

