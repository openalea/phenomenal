import numpy
import math
import collections

cdef list c_get_voxel_corners(voxel_center, voxel_size):

    cdef float r = voxel_size / 2.0
    cdef float x_minus = voxel_center[0] - r
    cdef float x_plus = voxel_center[0] + r
    cdef float y_minus = voxel_center[1] - r
    cdef float y_plus = voxel_center[1] + r
    cdef float z_minus = voxel_center[2] - r
    cdef float z_plus = voxel_center[2] + r

    return [(x_minus, y_minus, z_minus),
            (x_plus, y_minus, z_minus),
            (x_minus, y_plus, z_minus),
            (x_minus, y_minus, z_plus),
            (x_plus, y_plus, z_minus),
            (x_plus, y_minus, z_plus),
            (x_minus, y_plus, z_plus),
            (x_plus, y_plus, z_plus)]

def c_get_bounding_box_voxel_projected(voxel_center, voxel_size, projection):

    voxel_corners = c_get_voxel_corners(voxel_center, voxel_size)
    pt_projected = [projection(voxel_corner) for voxel_corner in voxel_corners]
    lx, ly = zip(*pt_projected)

    return min(lx), max(lx), min(ly), max(ly)


def c_kept_visible_voxel(voxels_position,
                       voxels_size,
                       image_views,
                       error_tolerance=0):

    kept = collections.deque()
    for voxel_position in voxels_position:
        negative_weight = 0
        for image_view in image_views:
            if not c_voxel_is_visible_in_image(
                    voxel_position,
                    voxels_size,
                    image_view.image,
                    image_view.projection,
                    image_view.inclusive):
                negative_weight += 1
                if negative_weight > error_tolerance:
                    break

        if negative_weight <= error_tolerance:
            kept.append(voxel_position)

    return kept

def c_voxel_is_visible_in_image(voxel_center,
                               voxel_size,
                               image,
                               projection,
                               inclusive):

    height_image, length_image = image.shape
    x, y = projection(voxel_center)

    if (0 <= x < length_image and
        0 <= y < height_image and
            image[int(y), int(x)] > 0):
        return True

    # ==========================================================================

    x_min, x_max, y_min, y_max = c_get_bounding_box_voxel_projected(
        voxel_center, voxel_size, projection)

    if (x_max < 0 or x_min >= length_image or
            y_max < 0 or y_min >= height_image):
        return inclusive

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