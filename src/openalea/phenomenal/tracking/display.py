"""3D visualisation using VTK, and color palette for leaf ranks"""

import numpy as np

# colors used to visualize leaf ranks
PALETTE = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [204, 121, 167],
    [0, 158, 115],
    [0, 114, 178],
    [230, 159, 0],
    [140, 86, 75],
    [0, 255, 255],
    [255, 0, 100],
    [0, 77, 0],
    [100, 0, 255],
    [100, 0, 0],
    [0, 0, 100],
    [100, 100, 0],
    [0, 100, 100],
    [100, 0, 100],
    [0, 0, 0],
    [255, 100, 100],
]
PALETTE = np.array(3 * PALETTE + [[255, 255, 255]])


def plot_polylines(polylines, ranks):
    """Display polylines colored by leaf rank, until the window is closed.

    Parameters
    ----------
    polylines : sequence of array-like, each of shape (M, 3)
        The points of each polyline.
    ranks : sequence of int
        The rank of each polyline, or a single rank for all of them. Ranks
        below 1 mean an unknown rank, and are displayed in grey.
    """
    # the display package needs matplotlib, which PALETTE users may not have
    from ..display import show_polylines

    colors = [PALETTE[rank - 1] if rank > 0 else [90, 90, 90] for rank in ranks]
    show_polylines(polylines, colors=np.array(colors).reshape(-1, 3) / 255)
