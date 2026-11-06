# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""Benchmark the graph and skeletonize steps, VoxelGraph (scipy) API.

Same use and same skeleton files as _bench_skeleton_v0.py (networkx API,
code before the VoxelGraph class), so that both versions can be compared:

    # with the old code
    python test/test_segmentation/_bench_skeleton_v0.py grid.csv 8 4 --save ref
    # with the new code
    python test/test_segmentation/_bench_skeleton.py grid.csv 8 4 --compare ref

Times each step: create_graph, connect_all_node_with_nearest_neighbors and
skeletonize. --compare describes the differences segment by segment: tip
offset, distance between the polylines and overlap of the voxels.
"""
import argparse
import pickle
import sys
import time
from pathlib import Path

import numpy
import scipy.spatial

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.segmentation as phm_seg

sys.path.insert(0, str(Path(__file__).parent))
from _bench_skeleton_v0 import coarser, skeleton_data  # noqa: E402


def compare(reference, current, voxels_size):
    """Describe the differences between two skeleton_data, segment by segment.

    Each current segment is matched with the reference segment of closest tip
    (last polyline point). Distances are in voxels.
    """
    if reference == current:
        return "identical"
    tips = numpy.array([polyline[-1] for polyline, _ in reference])
    rows = []
    for polyline, voxels in current:
        k = int(numpy.argmin(numpy.linalg.norm(tips - polyline[-1], axis=1)))
        ref_polyline, ref_voxels = reference[k]
        tip = numpy.linalg.norm(numpy.subtract(polyline[-1], ref_polyline[-1]))
        distance, _ = scipy.spatial.cKDTree(ref_polyline).query(polyline)
        overlap = len(voxels & ref_voxels) / len(voxels | ref_voxels)
        rows.append((tip / voxels_size, distance.mean() / voxels_size, overlap))
    tip, distance, overlap = numpy.array(rows).T
    return (
        f"segments {len(reference)} -> {len(current)}, "
        f"same tip {int(numpy.sum(tip == 0))}, "
        f"tip offset median {numpy.median(tip):.1f} max {tip.max():.1f}, "
        f"polyline distance mean {distance.mean():.2f} max {distance.max():.2f}, "
        f"voxel overlap median {numpy.median(overlap):.3f} min {overlap.min():.3f}"
    )


def bench(name, voxel_grid, save=None, reference=None):
    timings = {}
    start = time.perf_counter()
    graph = phm_seg.create_graph(voxel_grid.voxels_position, voxel_grid.voxels_size)
    timings["create_graph"] = time.perf_counter() - start
    start = time.perf_counter()
    graph = phm_seg.connect_all_node_with_nearest_neighbors(graph)
    timings["connect"] = time.perf_counter() - start
    start = time.perf_counter()
    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)
    timings["skeletonize"] = time.perf_counter() - start
    print(
        f"{name}: {len(voxel_grid.voxels_position)} voxels, "
        f"{graph.number_of_edges()} edges, "
        + ", ".join(f"{k} {v:.2f} s" for k, v in timings.items())
        + f", {len(voxel_skeleton.segments)} segments",
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
            ref = pickle.load(f)
        print("  compared to reference:", compare(ref, data, voxel_grid.voxels_size))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", help="voxel grid file")
    parser.add_argument("sizes", nargs="*", type=float, help="voxel sizes (mm)")
    parser.add_argument("--save", help="directory to save the skeletons")
    parser.add_argument("--compare", help="directory of the reference skeletons")
    args = parser.parse_args()
    options = dict(save=args.save, reference=args.compare)
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
