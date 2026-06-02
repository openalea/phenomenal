# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================

import collections
import cv2
import scipy.spatial
import numpy

from ..object import VoxelGrid, ImageView

# ==============================================================================
# Class

Voxels = collections.namedtuple("Voxels", ["position", "size"])

# ==============================================================================
# deprecated numpy-python slow integral (kept as explicit 'doc' of what integral image is for us)


def get_integrale_image(img):
    a = numpy.zeros_like(img, dtype=int)
    a[img > 0] = 1
    for y, x in numpy.ndindex(a.shape):
        if x - 1 >= 0:
            a[y, x] += a[y, x - 1]
        if y - 1 >= 0:
            a[y, x] += a[y - 1, x]
        if x - 1 >= 0 and y - 1 >= 0:
            a[y, x] -= a[y - 1, x - 1]
    return a


def integral_image(input_array):
    binary = (input_array > 0).astype(numpy.uint8)
    integral = cv2.integral(binary, sdepth=cv2.CV_32S)
    return integral[1:, 1:]


def find_best_angle(bin_side_images):
    max_len = 0
    max_angle = None

    for angle in bin_side_images:
        x_pos, y_pos, x_len, y_len = cv2.boundingRect(
            cv2.findNonZero(bin_side_images[angle])
        )

        if x_len > max_len:
            max_len = x_len
            max_angle = angle

    return max_angle


def get_voxels_corners(voxels_position, voxels_size):
    """Return the coordinates of the 8 corners of each voxel.

    Parameters
    ----------
    voxels_position : numpy.ndarray, shape (N, 3)
        Center coordinates of the voxels.

    voxels_size : float
        Edge length of the cubic voxels.

    Returns
    -------
    corners : numpy.ndarray, shape (N, 8, 3)
        Corner coordinates for each voxel.

        ``corners[i, j]`` is the j-th corner of voxel i, with corners
        ordered as::

            0: (x-r, y-r, z-r)
            1: (x+r, y-r, z-r)
            2: (x-r, y+r, z-r)
            3: (x-r, y-r, z+r)
            4: (x+r, y+r, z-r)
            5: (x+r, y-r, z+r)
            6: (x-r, y+r, z+r)
            7: (x+r, y+r, z+r)

        where ``r = voxels_size / 2``.
    """

    r = voxels_size / 2.0

    x_minus = voxels_position[:, 0] - r
    x_plus = voxels_position[:, 0] + r
    y_minus = voxels_position[:, 1] - r
    y_plus = voxels_position[:, 1] + r
    z_minus = voxels_position[:, 2] - r
    z_plus = voxels_position[:, 2] + r

    corners = numpy.stack(
        (
            numpy.column_stack((x_minus, y_minus, z_minus)),
            numpy.column_stack((x_plus,  y_minus, z_minus)),
            numpy.column_stack((x_minus, y_plus,  z_minus)),
            numpy.column_stack((x_minus, y_minus, z_plus)),
            numpy.column_stack((x_plus,  y_plus,  z_minus)),
            numpy.column_stack((x_plus,  y_minus, z_plus)),
            numpy.column_stack((x_minus, y_plus,  z_plus)),
            numpy.column_stack((x_plus,  y_plus,  z_plus)),
        ),
        axis=1,
    )

    return corners


def get_bounding_box_voxel_projected(voxels_position, voxels_size, projection):
    """Compute projected bounding boxes of voxels.

    Parameters
    ----------
    voxels_position : numpy.ndarray, shape (N, 3)
        Center position of the voxels.

    voxels_size : float
        Edge length of the cubic voxels.

    projection : callable
        Function taking an array of 3D points of shape (M, 3) and returning
        an array of projected points of shape (M, 3), where each row is
        (u, v, depth).

    Returns
    -------
    bbox : numpy.ndarray, shape (N, 4)
        Bounding boxes of the projected voxels::

            [[x_min, y_min, x_max, y_max],
             ...]

    fully_in_front : numpy.ndarray, shape (N,)
        Boolean array indicating whether all voxel corners are in front of
        the camera (depth > 0).
    """

    voxels_corners = get_voxels_corners(voxels_position, voxels_size)
    n_voxels = voxels_corners.shape[0]

    # Project all corners
    pt = projection(voxels_corners.reshape(-1, 3))

    # (N*8, 3) -> (N, 8, 3)
    pt = pt.reshape(n_voxels, 8, 3)

    # All corners are in front of the camera
    fully_in_front = numpy.all(pt[:, :, 2] > 0, axis=1)

    # Bounding boxes from projected coordinates
    uv = pt[:, :, :2]

    bbox = numpy.column_stack(
        (
            uv[:, :, 0].min(axis=1),
            uv[:, :, 1].min(axis=1),
            uv[:, :, 0].max(axis=1),
            uv[:, :, 1].max(axis=1),
        )
    )

    return bbox, fully_in_front


# ==============================================================================


def split_voxels_in_eight(voxels):
    """Split each voxel in 8 en return the numpy.array position

          _ _ _ _ _ _ _ _ _                              _ _ _ _ _ _ _ _ _
        /                  /|                          /        /         /|
       /                  / |                         /--------/---------/ |
      /_ _ _ _ _ _ _ _ _ /  |                        /_ _ _ _ / _ _ _ _ /| |
     |                  |   |                       |        |         | |/|
     |                  |   |       =======>        |        |         | / |
     |                  |   |                       |_ _ _ _ | _ _ _ _ |/| |
     |                  |  /                        |        |         | |/
     |                  | /                         |        |         | /
     | _ _ _ _ _ _ _ _ _|/                          |_ _ _ _ | _ _ _ _ |/



    Parameters
    ----------
    voxels : Voxels
        Where position is a numpy.array([[x, y, z], ...] containing the center
        position of each voxel and size the diameter size value (float) of each
        voxel.

    Returns
    -------
    voxels : Voxels
    """
    if len(voxels.position) == 0:
        return Voxels(voxels.position, voxels.size / 2.0)

    r = voxels.size / 4.0

    x_minus = voxels.position[:, 0] - r
    x_plus = voxels.position[:, 0] + r
    y_minus = voxels.position[:, 1] - r
    y_plus = voxels.position[:, 1] + r
    z_minus = voxels.position[:, 2] - r
    z_plus = voxels.position[:, 2] + r

    a1 = numpy.column_stack((x_minus, y_minus, z_minus))
    a2 = numpy.column_stack((x_plus, y_minus, z_minus))
    a3 = numpy.column_stack((x_minus, y_plus, z_minus))
    a4 = numpy.column_stack((x_minus, y_minus, z_plus))
    a5 = numpy.column_stack((x_plus, y_plus, z_minus))
    a6 = numpy.column_stack((x_plus, y_minus, z_plus))
    a7 = numpy.column_stack((x_minus, y_plus, z_plus))
    a8 = numpy.column_stack((x_plus, y_plus, z_plus))

    return Voxels(
        numpy.concatenate((a1, a2, a3, a4, a5, a6, a7, a8), axis=0),
        voxels.size / 2.0
    )


# ==============================================================================
def image_hits(points, image, projection):
    """Determine if projection of points on image hits foreground

    Args:
        points: (N, 3) array of x,y,z positions of points
        image: a binary image
        projection: a function of (N, 3) array returning (u, v), depth arrays


    Returns:
        boolean array(N,) -> True if projection is on image and hits a pixel > 0
    """
    height, width = image.shape
    N = len(points)

    mask = numpy.zeros(N, dtype=bool)

    uvd= projection(points)
    px = uvd[:, 0]
    py = uvd[:, 1]
    depth = uvd[:, 2]

    outside = (
            (depth <= 0)
            | (px < 0)
            | (py < 0)
            | (px >= width)
            | (py >= height)
    )

    idx = numpy.nonzero(~outside)[0]

    if idx.size > 0:
        pix_x = px[idx].astype(numpy.int32)
        pix_y = py[idx].astype(numpy.int32)
        mask[idx] = image[pix_y, pix_x] > 0

    return mask


def is_fully_inside(boxes, width, height):
    """Return True for boxes entirely contained within the image.

    Parameters
    ----------
    boxes : numpy.ndarray, shape (N, 4)
        Boxes in the form [x_min, x_max, y_min, y_max].

    width : int
        Image width.

    height : int
        Image height.

    Returns
    -------
    inside : numpy.ndarray, shape (N,)
        True for boxes whose four corners lie inside the image.
    """

    return (
        (boxes[:, 0] >= 0) &
        (boxes[:, 2] < width) &
        (boxes[:, 1] >= 0) &
        (boxes[:, 3] < height)
    )

def integral_image_hits(boxes, image_int, width, height):
    """
    boxes: (N, 4) array → [x_min, y_min, x_max, y_max] (float or int)
    returns: boolean array (N,) → True if any pixel inside box > 0
    """

    if len(boxes) == 0:
        return numpy.zeros(0, dtype=bool)

    # Floor + convert once
    boxes = numpy.floor(boxes).astype(numpy.int32)

    # Clip to image bounds
    boxes[:, 0] = numpy.clip(boxes[:, 0], 0, width - 1)
    boxes[:, 2] = numpy.clip(boxes[:, 2], 0, width - 1)
    boxes[:, 1] = numpy.clip(boxes[:, 1], 0, height - 1)
    boxes[:, 3] = numpy.clip(boxes[:, 3], 0, height - 1)

    # Integral image offset trick
    boxes[:, 0:2] -= 1
    boxes[boxes < 0] = 0

    x0 = boxes[:, 0]
    y0 = boxes[:, 1]
    x1 = boxes[:, 2]
    y1 = boxes[:, 3]

    # Vectorized integral image query
    sums = (
        image_int[y1, x1]
        + image_int[y0, x0]
        - image_int[y0, x1]
        - image_int[y1, x0]
    )

    return sums > 0


def voxels_is_visible_in_image(
    voxels_position, voxels_size, image, image_int, projection, inclusive=True):
    """
    Return a numpy array containing True if the voxels are fully in front of the camera and contains at least
    one foreground pixel. If inclusive = True (default), return also True for voxels that are undetermined,
    ie that are partly or totally outside image (only empty fully visible voxels return False in this case).

    Args:
    voxels_position : numpy.array([[x, y, z], ...]
        Center position of the voxels

    voxels_size : float
        edge length of voxels

    image: numpy.array
        Binary image where the voxels are projected.

    projection : function (numpy.array([[x, y, z], ...]) -> numpy.array([[u, v, depth], ...])
        Function of projection who take 1 argument (numpy.array([[x, y, z],
        ...] of voxels positions) and return the projected position

    inclusive: the boolean value returned for voxels partly of totally projected out of the image

    image_int: Integral image of the binary image

    Returns:
        A boolean array as long as voxels_position
    """
    height, width = image.shape
    N = len(voxels_position)
    if not inclusive:
        mask = image_hits(voxels_position, image, projection)
        no_hits = ~mask
        if numpy.any(no_hits):
            boxes, fully_in_front = get_bounding_box_voxel_projected(voxels_position[no_hits], voxels_size, projection)
            not_empty = integral_image_hits(boxes,image_int, width, height)
            mask[no_hits] = fully_in_front & not_empty
    else:
        mask = numpy.ones(N, dtype=bool)
        boxes, fully_in_front = get_bounding_box_voxel_projected(voxels_position, voxels_size, projection)
        fully_inside = is_fully_inside(boxes, width, height)
        fully_visible = fully_in_front & fully_inside
        if numpy.any(fully_visible):
             not_empty = integral_image_hits(
                boxes[fully_visible],
                image_int,
                width,
                height)
             mask[fully_visible] = not_empty # False is returned for empty, ie when not_empty=False
    return mask



# ==============================================================================
def reconstruction_grid(center=(0.0, 0.0, 0.0), grid_size=4096, voxel_size=512):
    """
    Setup a reconstruction grid
    Args:
        center: coordinates of the center of the grid
        grid_size: outer edge length of the grid
        voxel_size: edge length of voxels composing the grid

    Returns:
        a Voxels (positions, size) named tuple
    """
    voxels_position = numpy.array([center])
    voxels = Voxels(voxels_position, grid_size)
    while voxels.size != voxel_size:
        voxels = split_voxels_in_eight(voxels)
    return voxels


def check_each(image_views, check=True):
    """Return a check dict for all keys in image_views according to check

    Args:
        image_views : {name: ImageView, ...}
         Dict of phenomenal.object.ImageView objects gathering image, projection, where image is a binary image
         (numpy.ndarray) and projection a function projecting (x, y, z) ->  (u, v) coordinate on image
        check: bool | str | [str,...]
         If True or False, the value associated to each key present in image_views. If a list of name,
         the names to be set to True
    """
    if isinstance(check, bool):
        return {k: check for k in image_views}

    check = [check] if isinstance(check, str) else check

    return {
        name: any(name.startswith(cam) for cam in check)
        for name in image_views
    }


def filter_voxels(voxels, image_views, error_tolerance=0, clear_outside=True):
    """Filter voxels, keeping the one photo_consistent with all minus error_tolerance images in image_views"""

    clear_view = check_each(image_views, clear_outside)
    photo_consistent_score = numpy.zeros((len(voxels.position),), dtype=int)
    for i, (k, image_view) in enumerate(image_views.items()):
        if image_view.integral is None:
            image_view.integral = integral_image(image_view.image)
        inclusive = not clear_view[k]
        photo_consistent_score += voxels_is_visible_in_image(
            voxels_position=voxels.position,
            voxels_size=voxels.size,
            image=image_view.image,
            projection=image_view.projection,
            inclusive=inclusive,
            image_int=image_view.integral
        )
        cond = photo_consistent_score >= i + 1 - error_tolerance
        voxels = Voxels(voxels.position[cond], voxels.size)
        photo_consistent_score = photo_consistent_score[cond]

    return voxels


def tolerant_reconstruction(image_views, voxels_size=4, error_tolerance=0, clear_outside=None, start=None):

    if start is None:
        voxels = reconstruction_grid()
    elif isinstance(start, VoxelGrid):
        voxels = Voxels(start.voxels_position, start.voxels_size)
    else:
        voxels = start

    while voxels.size > voxels_size:
        if len(voxels.position) == 0:
            break
        voxels = split_voxels_in_eight(voxels)
        voxels = filter_voxels(voxels, image_views, error_tolerance=error_tolerance, clear_outside=clear_outside)

    return voxels


def multi_tolerant_reconstruction(image_views, voxels_size=4, max_tolerance=0, clear_outside=None, start=None):
    voxels = tolerant_reconstruction(image_views, voxels_size=voxels_size, error_tolerance=0, clear_outside=clear_outside,
                                     start=start)
    not_reconstructed = {}
    for k, iv in image_views.items():
        projected = project_voxel_centers_on_image(
            voxels.position,
            voxels.size,
            iv.image.shape,
            iv.projection,
        )
        view = ImageView(numpy.logical_not(projected)*255,
                            iv.projection)
        not_reconstructed[k] = view

    for i in range(max_tolerance):
        new_voxels = reconstruction_grid()
        while new_voxels.size > voxels_size:
            if len(new_voxels.position) == 0:
                break
            new_voxels = split_voxels_in_eight(new_voxels)
            new_voxels = filter_voxels(new_voxels, image_views, error_tolerance=i + 1, clear_outside=clear_outside)
            new_voxels = filter_voxels(new_voxels, not_reconstructed, error_tolerance=0, clear_outside=clear_outside)

        if len(new_voxels.position) == 0:
            break

        for k, iv in image_views.items():
            projected = project_voxel_centers_on_image(
                new_voxels.position,
                new_voxels.size,
                iv.image.shape,
                iv.projection,
            )
            not_reconstructed[k].image *= numpy.logical_not(projected)

        voxels = Voxels(numpy.concatenate((voxels.position, new_voxels.position), axis=0), voxels.size)

    return voxels


def reconstruction_3d(
    image_views,
    voxels_size=4,
    error_tolerance=0,
    start=None,
    clear_outside=True
):
    """
    Construct a list of voxel represented object with positive value on binary
    image in images of images_projections.

    Parameters
    ----------

    image_views : {name: ImageView, ...}
        Dict of phenomenal.object.ImageView objects gathering image, projection, where image is a binary image
        (numpy.ndarray) and projection a function projecting (x, y, z) ->  (u, v), depth coordinate on image

    voxels_size : float, optional
        Edge length of reconstructed voxels

    error_tolerance : int, optional
        Control the degree of consistency of the reconstructed object with its projected views
        If not provided the reconstruction is fully consistent with all views (error_tolerance=0)
        If positive, the number of inconsistent views tolerated per voxel
        If negative, a composite 3d reconstruction is computed, iteratively aggregating reconstructions of different
        tolerance, from zero to abs(error_tolerance), discarding at each step voxels projecting on projections of
        already reconstructed

    start : VoxelGrid | [Voxel,..], optional
        A voxel grid to be used as starting point.
        If None (default), a grid returned by defaults of openalea.phenomenal.multiview_reconstruction.reconstruction_grid

    clear_outside: bool | str | [str,...], optional
        Should voxels projected outside image_views be kept ? True (default) or False set a unique rule for all views.
        if a list of name is provided, only image_views whose key starts with names are used to clear voxels


    Returns
    -------
    out : VoxelGrid
    """

    if len(image_views) == 0:
        raise ValueError("Images views is empty")

    if error_tolerance >= 0:
        voxels = tolerant_reconstruction(image_views, voxels_size=voxels_size, error_tolerance=error_tolerance,
                                           start=start, clear_outside=clear_outside)
    else:
        voxels = multi_tolerant_reconstruction(image_views, voxels_size=voxels_size, max_tolerance=abs(error_tolerance),
                                           start=start, clear_outside=clear_outside)

    return VoxelGrid(voxels.position, voxels.size)

# ==============================================================================


def project_voxel_centers_on_image(
    voxels_position, voxels_size, shape_image, projection, value=255, dtype=numpy.uint8
):
    """
    Create a image with same shape that shape_image and project each voxel on
    image and write positive value (255) on it.

    Parameters
    ----------
    voxels_position : numpy.ndarray
        Voxels center position [[x, y, z], ...]
    voxels_size : float
        Diameter size of the voxels
    shape_image: 2-tuple
        Size height and width of the image target projected
    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)
    value : int
        value between 0 and 255 of positive pixel. By default, 255.
    dtype : type
        numpy type of the returned image. By default, numpy.uint8.

    Returns
    -------
    out : numpy.ndarray
        Binary image
    """
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=dtype)

    min_xy_max_xy, _ = get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection
    )

    vv = (
        (min_xy_max_xy[:, 2] < 0)
        | (min_xy_max_xy[:, 0] >= length)
        | (min_xy_max_xy[:, 3] < 0)
        | (min_xy_max_xy[:, 1] >= height)
    )

    not_vv = numpy.logical_not(vv)
    min_xy_max_xy = min_xy_max_xy[not_vv]

    min_xy_max_xy = numpy.floor(min_xy_max_xy)
    min_xy_max_xy[min_xy_max_xy < 0] = 0
    (min_xy_max_xy[:, 0])[min_xy_max_xy[:, 0] >= length] = length - 1
    (min_xy_max_xy[:, 1])[min_xy_max_xy[:, 1] >= height] = height - 1
    (min_xy_max_xy[:, 2])[min_xy_max_xy[:, 2] >= length] = length - 1
    (min_xy_max_xy[:, 3])[min_xy_max_xy[:, 3] >= height] = height - 1
    min_xy_max_xy = min_xy_max_xy.astype(int)

    for x_min, y_min, x_max, y_max in min_xy_max_xy:
        img[y_min : y_max + 1, x_min : x_max + 1] = value

    return img


def project_voxels_position_on_image(
    voxels_position, voxels_size, shape_image, projection
):
    """
    Create an image with same shape that shape_image and project each voxel on
    image and write positive value (255) on it.

    Parameters
    ----------
    voxels_position : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxels_size : float
        Size of side geometry of voxel

    shape_image: Tuple
        size height and length of the image target projected

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : numpy.ndarray
        Binary image
    """

    voxels_position = numpy.array(voxels_position)
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    voxels_corners = get_voxels_corners(voxels_position, voxels_size)
    pt = projection(voxels_corners)
    pt = numpy.reshape(pt, (pt.shape[0] // 8, 8, 2))

    pt[pt < 0] = 0
    (pt[:, :, 0])[pt[:, :, 0] >= length] = length - 1
    (pt[:, :, 1])[pt[:, :, 1] >= height] = height - 1
    pt = numpy.floor(pt).astype(int)
    for points in pt:
        hull = scipy.spatial.ConvexHull(points)
        cv2.fillConvexPoly(img, points[hull.vertices], 255)

    return img


# ==============================================================================


def image_error(img_ref, img_src, precision=2):
    """
    Return false position and true negative result from the comparison on
    two binaries images
    """

    img_ref = img_ref.astype(numpy.int32)
    nb_ref = max(numpy.count_nonzero(img_ref), 1)
    nb_ref2 = max(numpy.count_nonzero(img_ref == 0), 1)
    img_src = img_src.astype(numpy.int32)
    img = numpy.subtract(img_ref, img_src)
    true_negative = numpy.bitwise_and(img_ref == 0, img_src == 0)
    true_negative = round(
        numpy.count_nonzero(true_negative) * 100.0 / nb_ref2, precision
    )
    # true_negative = numpy.bitwise_and(img_ref == 0, img_src == 0)

    false_positive = round(
        numpy.count_nonzero(img[img < 0]) * 100.0 / nb_ref2, precision
    )
    false_negative = round(
        numpy.count_nonzero(img[img > 0]) * 100.0 / nb_ref, precision
    )
    print(true_negative, false_positive, false_negative)
    return false_positive, false_negative


def reconstruction_error(voxels_grid, image_views):
    """
    Compute the reconstruction error (false positive and true negative) of
    the 3d reconstruction from the image view.

    Parameters
    ----------
    voxels_grid: VoxelGrid
        The voxel grid

    image_views : numpy.ndarray[ImageView]
        An array of all image views
    Returns
    -------
    out : (float,float)
        A tuple with the mean false positive and the mean false negative
    """

    sum_false_positive = 0
    sum_false_negative = 0
    for image_view in image_views.values():
        img_src = project_voxel_centers_on_image(
            voxels_grid.voxels_position,
            voxels_grid.voxels_size,
            image_view.image.shape,
            image_view.projection,
        )

        false_positive, false_negative = image_error(image_view.image, img_src)

        sum_false_positive += false_positive
        sum_false_negative += false_negative

    mean_false_positive = sum_false_positive / len(image_views)
    mean_false_negative = sum_false_negative / len(image_views)

    return mean_false_positive, mean_false_negative



