# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""Benchmark graph_from_voxel_grid and skeletonize, networkx graph API.

For the code where graph_from_voxel_grid returns a networkx.Graph: master up
to 8e4c266 (November 2026) and the releases up to 1.9.5. The script stays in
this checkout and imports the old phenomenal. Saves each skeleton, so that
_bench_skeleton.py (VoxelGraph code) can compare its skeletons with them.

To run it on master 8e4c266, check that commit out in a separate folder and
put its src first on the python path (networkx must be installed, as skan
already requires it). From the root of this checkout:

    git worktree add ../phenomenal_networkx 8e4c266
    PYTHONPATH=../phenomenal_networkx/src python test/test_segmentation/_bench_skeleton_networkx.py grid.csv 8 4 --save ref
    python test/test_segmentation/_bench_skeleton.py grid.csv 8 4 --compare ref
    git worktree remove ../phenomenal_networkx

In the Anaconda Prompt (cmd), set the path on its own line, and clear it
before running _bench_skeleton.py:

    set PYTHONPATH=../phenomenal_networkx/src
    python test/test_segmentation/_bench_skeleton_networkx.py grid.csv 8 4 --save ref
    set PYTHONPATH=
    python test/test_segmentation/_bench_skeleton.py grid.csv 8 4 --compare ref

The first line each script prints says which phenomenal it imports.

With no file, uses the voxel grids of test/data/plant_1 (32 and 16 mm).
With a voxel grid file (.csv, .npz, .json), the grid is merged into
coarser voxels of each given size (mm), or used as is with no size.
--save DIR writes one skeleton file per grid in DIR; --compare DIR
compares each skeleton with the one saved in DIR.
"""
import argparse
import pickle
import time
from pathlib import Path

import numpy

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.segmentation as phm_seg


def coarser(voxel_grid, voxels_size):
    """Merge voxels into voxels of size voxels_size (voxel centers)."""
    position = numpy.asarray(list(voxel_grid.voxels_position), dtype=float)
    corner = position - voxel_grid.voxels_size / 2
    cells = numpy.unique(numpy.floor(corner / voxels_size), axis=0)
    return phm_obj.VoxelGrid(cells * voxels_size + voxels_size / 2, voxels_size)


def skeleton_data(voxel_skeleton):
    """Plain python data of a skeleton: polyline and voxels of each segment."""
    return [
        (
            [tuple(map(float, p)) for p in segment.polyline],
            {tuple(map(float, v)) for v in segment.voxels_position},
        )
        for segment in voxel_skeleton.segments
    ]


def compare(reference, current):
    """Describe the differences between two skeleton_data."""
    if reference == current:
        return "identical"
    ref_voxels = set().union(*(v for _, v in reference))
    cur_voxels = set().union(*(v for _, v in current))
    ref_polylines = {tuple(p) for p, _ in reference}
    same_polylines = sum(tuple(p) in ref_polylines for p, _ in current)
    jaccard = len(ref_voxels & cur_voxels) / max(len(ref_voxels | cur_voxels), 1)
    return (
        f"different: segments {len(reference)} -> {len(current)}, "
        f"{same_polylines} identical polylines, "
        f"voxels in segments {len(ref_voxels)} -> {len(cur_voxels)} "
        f"(overlap {jaccard:.4f})"
    )


def bench(name, voxel_grid, save=None, reference=None):
    start = time.perf_counter()
    graph = phm_seg.graph_from_voxel_grid(voxel_grid)
    graph_time = time.perf_counter() - start
    start = time.perf_counter()
    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)
    skeleton_time = time.perf_counter() - start
    print(
        f"{name}: {len(voxel_grid.voxels_position)} voxels, "
        f"graph {graph_time:.2f} s, skeletonize {skeleton_time:.2f} s, "
        f"{len(voxel_skeleton.segments)} segments",
        flush=True,
    )
    data = skeleton_data(voxel_skeleton)
    filename = name.replace(" ", "_") + ".pkl"
    if save is not None:
        Path(save).mkdir(parents=True, exist_ok=True)
        with open(Path(save) / filename, "wb") as f:
            pickle.dump(data, f)
    if reference is not None:
        with open(Path(reference) / filename, "rb") as f:
            print("  compared to reference:", compare(pickle.load(f), data))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", help="voxel grid file")
    parser.add_argument("sizes", nargs="*", type=float, help="voxel sizes (mm)")
    parser.add_argument("--save", help="directory to save the skeletons")
    parser.add_argument("--compare", help="directory of the reference skeletons")
    args = parser.parse_args()
    options = dict(save=args.save, reference=args.compare)
    print("phenomenal from", Path(phm_seg.__file__).parents[1])
    if args.file is None:
        for size in (32, 16):
            voxel_grid = phm_data.voxel_grid(Path("test/data/plant_1"), size)
            bench(f"plant_1 {size}", voxel_grid, **options)
        return
    voxel_grid = phm_obj.VoxelGrid.read(args.file)
    stem = Path(args.file).stem
    if not args.sizes:
        bench(stem, voxel_grid, **options)
    for size in args.sizes:
        bench(f"{stem} {size:g}", coarser(voxel_grid, size), **options)


if __name__ == "__main__":
    main()
