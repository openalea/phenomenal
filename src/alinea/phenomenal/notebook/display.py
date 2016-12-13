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

import numpy as np
from IPython.display import display
from ipywidgets import HTML, Text
from traitlets import link, dlink
from itertools import chain

# ==============================================================================

def show_voxel_point_cloud(voxel_point_cloud):

    voxel_center = voxel_point_cloud.voxels_center
    voxel_size = voxel_point_cloud.voxels_size

    # Transform to vertices display format
    vertices = list(chain.from_iterable(voxel_center))

    # Define points
    geometry = BufferGeometry(vertices=vertices)
    # Define colors and size points
    material = PointsMaterial(size=voxel_size, color='green')

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
    renderer.width = "800"
    renderer.height = "600"
    # Define background color and opacity of window renderer
    renderer.background_color = "black"
    renderer.background_opacity = 0.5

    # launch display
    display(renderer)

