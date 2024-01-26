"""" 3D visualisation using PlantGL, and color palette for leaf ranks """

# %gui qt
import matplotlib.pyplot as plt
import numpy as np

has_pgl_display = True
try:
    from openalea.plantgl import all as pgl
except ImportError:
    has_pgl_display = False

# colors used to visualize leaf ranks
PALETTE = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [204, 121, 167], [0, 158, 115],
           [0, 114, 178], [230, 159, 0], [140, 86, 75], [0, 255, 255], [255, 0, 100], [0, 77, 0], [100, 0, 255],
           [100, 0, 0], [0, 0, 100], [100, 100, 0], [0, 100, 100], [100, 0, 100], [0, 0, 0], [255, 100, 100]]
PALETTE = np.array(3 * PALETTE + [[255, 255, 255]])


def plot_polylines(polylines, ranks):

    shapes = []

    for polyline, rank in zip(polylines, ranks):

        col_r, col_g, col_b = PALETTE[rank - 1] if rank > 0 else [90, 90, 90]
        col = pgl.Material(pgl.Color3(int(col_r), int(col_g), int(col_b)))

        r = 0  # 10 * np.random.random()
        for k in range(len(polyline) - 1):
            pos1 = np.array(polyline[k]) + np.array([0, 0, r])
            pos2 = np.array(polyline[k + 1]) + np.array([0, 0, r])
            cyl = pgl.Extrusion(pgl.Polyline([pos1, pos2]), pgl.Polyline2D.Circle(2, 8))
            cyl.solid = True
            cyl = pgl.Shape(cyl, col)
            shapes.append(cyl)

    scene = pgl.Scene(shapes)
    pgl.Viewer.display(scene)
