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
from __future__ import division, print_function

import collections
import math
import numpy
# ==============================================================================


def get_bounding_box_voxel_projected(voxel_center, voxel_size, projection):
    """
    Compute the bounding box value according the radius, angle and calibration
    parameters of point_3d projection

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : (x_min, x_max, y_min, y_max)
        Containing min and max value of point_3d projection in x and y axes.
    """

    voxel_corners = get_voxel_corners(voxel_center, voxel_size)
    pt_projected = [projection(voxel_corner) for voxel_corner in voxel_corners]
    lx, ly = zip(*pt_projected)

    return min(lx), max(lx), min(ly), max(ly)


def get_voxel_corners(voxel_center, voxel_size):
    """
    According center voxel position and this size, return a list of 8 corners
    of this voxel.

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    [(x, y, z), ...] : numpy.ndarray
         List of 8 tuple position

    """

    r = voxel_size / 2.0

    x_minus = voxel_center[0] - r
    x_plus = voxel_center[0] + r

    y_minus = voxel_center[1] - r
    y_plus = voxel_center[1] + r

    z_minus = voxel_center[2] - r
    z_plus = voxel_center[2] + r

    return [(x_minus, y_minus, z_minus),
            (x_plus, y_minus, z_minus),
            (x_minus, y_plus, z_minus),
            (x_minus, y_minus, z_plus),
            (x_plus, y_plus, z_minus),
            (x_plus, y_minus, z_plus),
            (x_minus, y_plus, z_plus),
            (x_plus, y_plus, z_plus)]

# ==============================================================================


def split_voxel_centers_in_eight(voxel_centers, voxel_size):
    """
    Split each voxel in the collections.deque in 8 en return a collections.deque
    of this new center position of voxel splited::

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
    voxel_centers : [(x, y, z)]
        collections.deque of center position of voxel

    voxel_size : float
        Size of side geometry of the voxels

    Returns
    -------
    [(x, y, z), ...] : collections.deque
         New collections.deque of new tuple position splited of each
         voxel_center in voxel_centers

    """
    if len(voxel_centers) == 0:
        return voxel_centers

    r = voxel_size / 4.0

    l = collections.deque()
    for voxel_center in voxel_centers:

        x_minus = voxel_center[0] - r
        x_plus = voxel_center[0] + r

        y_minus = voxel_center[1] - r
        y_plus = voxel_center[1] + r

        z_minus = voxel_center[2] - r
        z_plus = voxel_center[2] + r

        l.extend([(x_minus, y_minus, z_minus),
                  (x_plus, y_minus, z_minus),
                  (x_minus, y_plus, z_minus),
                  (x_minus, y_minus, z_plus),
                  (x_plus, y_plus, z_minus),
                  (x_plus, y_minus, z_plus),
                  (x_minus, y_plus, z_plus),
                  (x_plus, y_plus, z_plus)])

    return l


def split_voxel_centers_in_four(voxel_centers, voxel_size):
    """
    Split each voxel in the collections.deque in 4 en return a collections.deque
    of this new center position of voxel splited::

          _ _ _ _ _ _ _ _ _                              _ _ _ _ _ _ _ _ _
        /                  /|                          /        /         /|
       /                  / |                         /        /         / |
      /_ _ _ _ _ _ _ _ _ /  |                        /_ _ _ _ / _ _ _ _ /  |
     |                  |   |                       |        |         |  /|
     |                  |   |       =======>        |        |         | / |
     |                  |   |                       |_ _ _ _ | _ _ _ _ |/  |
     |                  |  /                        |        |         |  /
     |                  | /                         |        |         | /
     | _ _ _ _ _ _ _ _ _|/                          |_ _ _ _ | _ _ _ _ |/


    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        collections.deque of center position of voxel

    voxel_size : float
        Size of side geometry of the voxels

    Returns
    -------
    [(x, y, z), ...] : collections.deque
         New collections.deque of new tuple position splited of each
         voxel_center in voxel_centers

    """
    if len(voxel_centers) == 0:
        return voxel_centers

    r = voxel_size / 4.0

    l = collections.deque()
    for voxel_center in voxel_centers:
        x = voxel_center[0]

        y_minus = voxel_center[1] - r
        y_plus = voxel_center[1] + r

        z_minus = voxel_center[2] - r
        z_plus = voxel_center[2] + r

        l.extend([(x, y_minus, z_minus),
                  (x, y_minus, z_plus),
                  (x, y_plus, z_minus),
                  (x, y_plus, z_plus)])

    return l

# ==============================================================================


def voxel_is_visible_in_image(voxel_center,
                              voxel_size,
                              image,
                              projection):
    """
    Return True or False if the voxel projected on image with the function
    projection (projection) have positive value on image.

    **Algorithm**

    1. Project the center voxel position on image if the position projected
       (x, y) is positive on image return True

    |

    2. Project the bounding box of voxel in image, if one of the 4 corners
       position of the bounding box projected have positive value on image
       return True

    |

    3. Check if one pixel containing in the bounding box projected on image
       have positive value, if yes return True else return False

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    image: numpy.ndarray
        binary image

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : bool
        True if voxel have a positive correspondence on image otherwise return
        False
    """

    height_image, length_image = image.shape
    x, y = projection(voxel_center)

    if (0 <= x < length_image and
        0 <= y < height_image and
            image[int(y), int(x)] > 0):
        return True

    # ==========================================================================

    x_min, x_max, y_min, y_max = get_bounding_box_voxel_projected(
        voxel_center, voxel_size, projection)

    x_min = int(min(max(math.floor(x_min), 0), length_image - 1))
    x_max = int(min(max(math.ceil(x_max), 0), length_image - 1))
    y_min = int(min(max(math.floor(y_min), 0), height_image - 1))
    y_max = int(min(max(math.ceil(y_max), 0), height_image - 1))

    if (image[y_min, x_min] > 0 or
        image[y_max, x_min] > 0 or
        image[y_min, x_max] > 0 or
            image[y_max, x_max] > 0):
        return True

    # ==========================================================================

    if numpy.any(image[y_min:y_max + 1, x_min:x_max + 1] > 0):
        return True

    return False


def kept_visible_voxel(voxel_centers,
                       voxel_size,
                       images_projections,
                       error_tolerance=0):
    """
    Kept in a new collections.deque the voxel who is visible on each image of
    images_projections according the error_tolerance

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    images_projections : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    error_tolerance : int, optional
        Number of image will be ignored if the projected voxel is not visible.

    Returns
    -------
    out : collections.deque
        List of visible voxel projected on each image according
        the error_tolerance

    """
    kept = collections.deque()
    for voxel_center in voxel_centers:
        negative_weight = 0
        for image, projection in images_projections:
            if not voxel_is_visible_in_image(
                    voxel_center, voxel_size, image, projection):
                negative_weight += 1
                if negative_weight > error_tolerance:
                    break

        if negative_weight <= error_tolerance:
            kept.append(voxel_center)

    return kept

# ==============================================================================


def reconstruction_3d(images_projections,
                      voxel_size=4,
                      error_tolerance=0,
                      voxel_center_origin=(0.0, 0.0, 0.0),
                      world_size=4096,
                      voxel_centers=None,
                      verbose=False):
    """
    Construct a list of voxel represented object with positive value on binary
    image in images of images_projections.

    Parameters
    ----------
    images_projections : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    voxel_size : float, optional
        Size of side geometry of voxel that each voxel will have

    error_tolerance : int, optional


    voxel_center_origin : (x, y, z), optional
        Center position of the first original voxel, who will be split.

    world_size: int, optional
        Minimum size that the origin voxel size must include at beginning

    voxel_centers : collections.deque, optional
        List of first original voxel who will be split. If None, a list is
        create with the voxel_center_origin value.

    verbose : bool, optional
        If True, print for each iteration of split, number of voxel before and
        after projection on images

    Returns
    -------
    out : collections.deque
        List of visible voxel projected on each image according
        the error_tolerance
    """

    if len(images_projections) == 0:
        raise ValueError("images_projection list is empty")

    if voxel_centers is None:
        voxel_centers = collections.deque()
        voxel_centers.append(voxel_center_origin)

    nb_iteration = 0
    while voxel_size < world_size:
        voxel_size *= 2.0
        nb_iteration += 1

    for i in range(nb_iteration):

        if len(images_projections) == 1:
            voxel_centers = split_voxel_centers_in_four(voxel_centers,
                                                        voxel_size)
        else:
            voxel_centers = split_voxel_centers_in_eight(voxel_centers,
                                                         voxel_size)

        voxel_size /= 2.0

        if verbose is True:
            print('Iteration', i + 1, '/', nb_iteration, end="")
            print(' : ', len(voxel_centers), end="")

        voxel_centers = kept_visible_voxel(
            voxel_centers, voxel_size, images_projections, error_tolerance)

        if verbose is True:
            print(' - ', len(voxel_centers))

    return voxel_centers

# ==============================================================================


def project_voxel_centers_on_image(voxel_centers,
                                   voxel_size,
                                   shape_image,
                                   projection):
    """
    Create a image with same shape that shape_image and project each voxel on
    image and write positive value (255) on it.

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
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
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    for voxel_center in voxel_centers:
        x_min, x_max, y_min, y_max = get_bounding_box_voxel_projected(
            voxel_center, voxel_size, projection)

        x_min = int(min(max(math.floor(x_min), 0), length - 1))
        x_max = int(min(max(math.ceil(x_max), 0), length - 1))
        y_min = int(min(max(math.floor(y_min), 0), height - 1))
        y_max = int(min(max(math.ceil(y_max), 0), height - 1))

        img[y_min:y_max + 1, x_min:x_max + 1] = 255

    return img


def error_reconstruction(image_binary_ref,
                         projection,
                         voxel_centers,
                         voxel_size):
    """
    Project voxel_centers on a binary image and compare this image with
    image_binary_ref. Error is the number of all different pixel.

    Parameters
    ----------
    image_binary_ref: numpy.ndarray
        binary image reference

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    out : int
        Error value
    """
    img = project_voxel_centers_on_image(
        voxel_centers, voxel_size, image_binary_ref.shape, projection)

    img_src = img.astype(numpy.int32)
    img_ref = image_binary_ref.astype(numpy.int32)

    img = numpy.subtract(img_src, img_ref)
    img[img == -255] = 255
    img = img.astype(numpy.uint8)

    return numpy.count_nonzero(img)


def error_reconstruction_lost(image_binary_ref,
                              projection,
                              voxel_centers,
                              voxel_size):
    """
    Project voxel_centers on a binary image and compare this image with
    image_binary_ref. Error lost is the number of different pixel of
    image_binary_ref.

    Parameters
    ----------
    image_binary_ref: numpy.ndarray
        binary image reference

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    out : int
        Error value
    """
    img = project_voxel_centers_on_image(
        voxel_centers, voxel_size, image_binary_ref.shape, projection)

    img_src = img.astype(numpy.int32)
    img_ref = image_binary_ref.astype(numpy.int32)

    img = numpy.subtract(img_ref, img_src)
    img[img == -255] = 0
    img = img.astype(numpy.uint8)

    return numpy.count_nonzero(img)


def error_reconstruction_precision(image_binary_ref,
                                   projection,
                                   voxel_centers,
                                   voxel_size):
    """
    Project voxel_centers on a binary image and compare this image with
    image_binary_ref. Error precision is the number of different pixel of
    build binary image.

    Parameters
    ----------
    image_binary_ref: numpy.ndarray
        binary image reference

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    out : int
        Error value
    """
    img = project_voxel_centers_on_image(
        voxel_centers, voxel_size, image_binary_ref.shape, projection)

    img_src = img.astype(numpy.int32)
    img_ref = image_binary_ref.astype(numpy.int32)

    img = numpy.subtract(img_src, img_ref)
    img[img == -255] = 0
    img = img.astype(numpy.uint8)

    return numpy.count_nonzero(img)


def volume(voxel_centers, voxel_size):
    """
    Compute the volume of voxel list.

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    out : int
        Error value
    """
    return len(voxel_centers) * voxel_size**3
