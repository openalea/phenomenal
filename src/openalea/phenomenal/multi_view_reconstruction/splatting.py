""" Opensplat/phenomenal interface
"""
import struct
import json
import numpy as np
from pathlib import Path
import openalea.phenomenal.mesh as phm_mesh
from scipy.spatial import ConvexHull, Delaunay, cKDTree


#
# from phenomenal to opensplat : simulate colmap output
#
def export_as_colmap(calibration, image_paths, starting_mesh, colmap_dir):
    setup_dir = Path(colmap_dir) / 'sparse' / '0'
    setup_dir.mkdir(parents=True, exist_ok=True)

    cameras = calibration.colmap_cameras()
    with open(setup_dir / 'cameras.txt', 'w') as f:
        f.write(cameras)

    images = calibration.colmap_images(image_paths)
    with open(setup_dir / 'images.txt', 'w') as f:
        f.write(images)

    vertices, faces = starting_mesh
    centers = phm_mesh.centers(vertices, faces)
    with open(setup_dir / 'points3D.txt', 'w') as f:
        for i, (x, y, z) in enumerate(centers, start=1):
            f.write(
                f"{i} {x} {y} {z} 30 50 30 1.0 \n"
            )


#
# from opensplat to phenomenal
#
def read_splat(file: str):
    """
    Convert a .splat file to a point cloud
    Parameters
    ----------
    file: str
        The path to the splat file

    Returns
    -------
    position: np.array
        The position of each gaussians.
    colors: np.array
        The rgb colors of each gaussians.
    scale: np.array
        The scale of each gaussians.
    rotation: np.array
        The rotation of each gaussians in quaternion form.
    """
    # position: 3 floats (12 bytes)
    # scale: 3 floats (12 bytes)
    # rotation: 4 chars (4 bytes)
    # color+opacity: 4 chars (4 bytes)
    position_offset = 0
    scale_offset = 12
    color_offset = 24
    rotation_offset = 28

    splat_size = 32

    with open(file, "rb") as f:
        data = bytearray(f.read())

    n_splats = int(len(data) / splat_size)
    positions = []
    colors = []
    scales = []
    rotations = []
    for i in range(n_splats):
        position = struct.unpack(
            "fff", data[splat_size * i + position_offset : splat_size * i + 12]
        )
        positions.append(position)
        color = struct.unpack(
            "BBBB",
            data[splat_size * i + color_offset : splat_size * i + color_offset + 4],
        )
        colors.append(color)
        scale = struct.unpack(
            "fff",
            data[splat_size * i + scale_offset : splat_size * i + scale_offset + 12],
        )
        scales.append(scale)
        rot = struct.unpack(
            "BBBB",
            data[
                splat_size * i + rotation_offset : splat_size * i + rotation_offset + 4
            ],
        )
        rotations.append(rot)
    return np.array(positions), np.array(colors), np.array(scales), np.array(rotations)


def load_splat_cameras(json_filename):
    """
    Load camera centers from an opensplat/gaussian-splatting JSON file.

    Returns
    -------
    dict
        {
            image_name: {
                "id": int,
                "position": np.ndarray shape (3,),
                "rotation": np.ndarray shape (3, 3),
                "fx": float,
                "fy": float,
                "width": int,
                "height": int,
            }
        }
    """

    with open(json_filename, "r") as f:
        cameras = json.load(f)

    out = {}

    for cam in cameras:

        out[cam["img_name"]] = {
            "id": cam["id"],
            "position": np.asarray(cam["position"], dtype=float),
            "rotation": np.asarray(cam["rotation"], dtype=float),
            "fx": float(cam["fx"]),
            "fy": float(cam["fy"]),
            "width": int(cam["width"]),
            "height": int(cam["height"]),
        }

    return out


def qvec2rotmat(qvec):
    """
    Convert COLMAP quaternion to rotation matrix.

    COLMAP quaternion format:
        qw qx qy qz
    """
    qw, qx, qy, qz = qvec

    return np.array([
        [
            1 - 2 * qy**2 - 2 * qz**2,
            2 * qx * qy - 2 * qw * qz,
            2 * qx * qz + 2 * qw * qy,
        ],
        [
            2 * qx * qy + 2 * qw * qz,
            1 - 2 * qx**2 - 2 * qz**2,
            2 * qy * qz - 2 * qw * qx,
        ],
        [
            2 * qx * qz - 2 * qw * qy,
            2 * qy * qz + 2 * qw * qx,
            1 - 2 * qx**2 - 2 * qy**2,
        ],
    ])


def load_colmap_cameras(images_txt):
    """
    Read COLMAP images.txt camera poses.

    Parameters
    ----------
    images_txt : str or Path

    Returns
    -------
    dict
        {
            image_name: {
                "id": int,
                "camera_id": int,
                "qvec": np.ndarray shape (4,),
                "tvec": np.ndarray shape (3,),
                "rotation": np.ndarray shape (3, 3),
                "position": np.ndarray shape (3,),
            }
        }

    Notes
    -----
    COLMAP stores:
        X_cam = R * X_world + t

    Camera center in world coordinates is:
        C = -R.T @ t
    """

    cameras = {}

    with open(images_txt, "r") as f:

        lines = f.readlines()

    for line in lines:

        line = line.strip()

        # skip comments
        if not line or line.startswith("#"):
            continue

        fields = line.split()

        # image line has at least 10 fields
        if len(fields) < 10:
            continue

        # skip 2D point lines
        try:
            image_id = int(fields[0])
        except ValueError:
            continue

        qvec = np.array([
            float(fields[1]),
            float(fields[2]),
            float(fields[3]),
            float(fields[4]),
        ])

        tvec = np.array([
            float(fields[5]),
            float(fields[6]),
            float(fields[7]),
        ])

        camera_id = int(fields[8])

        image_name = fields[9]

        R = qvec2rotmat(qvec)

        # camera center in world coordinates
        C = -R.T @ tvec

        cameras[image_name] = {
            "id": image_id,
            "camera_id": camera_id,
            "qvec": qvec,
            "tvec": tvec,
            "rotation": R,
            "position": C,
        }

    return cameras


def similarity_transform(src, dst):
    """
    Estimate similarity transform such that:

        dst ~= s * R @ src + t
    """

    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)

    src_centered = src - src_mean
    dst_centered = dst - dst_mean

    H = src_centered.T @ dst_centered

    U, S, Vt = np.linalg.svd(H)

    R = Vt.T @ U.T

    if np.linalg.det(R) < 0:
        Vt[-1] *= -1
        R = Vt.T @ U.T

    var_src = np.sum(src_centered ** 2)

    scale = np.sum(S) / var_src

    t = dst_mean - scale * R @ src_mean

    return scale, R, t


def register_splat(xyz, cams_colmap, cams_splat):
    pos_colmap = np.array([
        cams_colmap[k]["position"]
        for k in sorted(cams_colmap)
    ])

    pos_splat = np.array([
        cams_splat[k]["position"]
        for k in sorted(cams_colmap)
    ])

    scale, R, t = similarity_transform(pos_splat, pos_colmap)

    return scale * (xyz @ R.T) + t


def filter_points_in_hull(
    xyz,
    reference_xyz,
    margin=0.02,
):
    """
    Keep points inside a dilated convex hull.

    Parameters
    ----------
    xyz : (N,3) array
        Points to filter.

    reference_xyz : (M,3) array
        Reference geometry.

    margin : float
        Isotropic dilation factor.
    """

    center = reference_xyz.mean(axis=0)

    # dilate hull points around center
    ref_dilated = (
        center +
        (reference_xyz - center) * (1.0 + margin)
    )

    hull = ConvexHull(ref_dilated)

    delaunay = Delaunay(ref_dilated[hull.vertices])

    mask = delaunay.find_simplex(xyz) >= 0

    return xyz[mask], mask


def estimate_spacing(reference_xyz, k=2):
    """
    Estimate typical point spacing from nearest neighbors.

    Returns
    -------
    float
        Median nearest-neighbor distance.
    """

    tree = cKDTree(reference_xyz)

    distances, _ = tree.query(reference_xyz, k=k)

    # k=2 because first neighbor is self
    nn_dist = distances[:, 1]

    return np.median(nn_dist)


def filter_low_density_points(
    xyz,
    radius,
    min_neighbors=5,
):
    """
    Remove isolated low-density points.

    Parameters
    ----------
    xyz : (N,3) array

    radius : float
        Neighborhood radius.

    min_neighbors : int
        Minimum number of neighbors required.

    Returns
    -------
    filtered_xyz : (K,3) array
    mask : (N,) bool
    """

    tree = cKDTree(xyz)

    neighbors = tree.query_ball_point(
        xyz,
        r=radius,
    )

    counts = np.array([
        len(n) - 1
        for n in neighbors
    ])

    mask = counts >= min_neighbors

    return xyz[mask], mask

def photo_consistent_filter(xyz, image_views, min_score=3):
    N = len(xyz)
    photo_consistent_score = np.zeros((N,), dtype=int)
    for iv in image_views:
        height, width = iv.image.shape
        mask = np.zeros(N, dtype=bool)
        pixel_coords = iv.projection(xyz)
        px = pixel_coords[:, 0]
        py = pixel_coords[:, 1]
        # In-bounds indices
        idx = np.nonzero(
            (px >= 0) & (py >= 0) & (px < width) & (py < height)
        )[0]
        if idx.size > 0:
            pix = pixel_coords[idx].astype(np.int32)
            mask[idx] |= iv.image[pix[:, 1], pix[:, 0]] > 0
        photo_consistent_score += mask
    return photo_consistent_score