# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


# ==============================================================================
class ImageView:
    """Container associating an image with its geometric projection.

    Attributes:
        image:
            Image array associated with a camera/view configuration.
        projection:
            Projection object/function returned by the calibration model for
            the corresponding camera and angle.
        integral:
            Optional cached integral image representation. Initialized to
            ``None`` and can be computed later for performance purposes.
    """

    def __init__(self, image, projection):
        """Initialize an ImageView instance.

        Args:
            image:
                Input image array.
            projection:
                Projection object/function describing the mapping associated
                with the image acquisition setup.
        """
        self.image = image
        self.projection = projection
        self.integral = None


def iter_image_paths(image_paths, imread, cameras=None, angles=None):
    """Iterate over images stored as file paths.

    Args:
        image_paths:
            Nested dictionary mapping camera identifiers and angles to image
            file paths::

                {
                    camera_id: {
                        angle: image_path,
                        ...
                    },
                    ...
                }

        imread:
            Callable used to read an image from a file path.
        cameras:
            Optional iterable of camera identifiers to filter.
            If ``None``, all cameras are used.
        angles:
            Optional iterable of view angles to filter.
            If ``None``, all angles are used.

    Yields:
        Tuples ``(camera_id, angle, image_array)`` for each selected image.
    """

    if cameras is not None:
        cameras = set(cameras)

    if angles is not None:
        angles = set(angles)

    for id_camera in image_paths:

        if cameras is not None and id_camera not in cameras:
            continue

        for angle in image_paths[id_camera]:

            if angles is not None and angle not in angles:
                continue

            yield id_camera, angle, imread(image_paths[id_camera][angle])


def iter_images(images, cameras=None, angles=None):
    """Iterate over an in-memory image dictionary.

    Args:
        images:
            Nested dictionary mapping camera identifiers and angles to image
            arrays::

                {
                    camera_id: {
                        angle: image_array,
                        ...
                    },
                    ...
                }

        cameras:
            Optional iterable of camera identifiers to filter.
            If ``None``, all cameras are used.
        angles:
            Optional iterable of view angles to filter.
            If ``None``, all angles are used.

    Yields:
        Tuples ``(camera_id, angle, image_array)`` for each selected image.
    """

    if cameras is not None:
        cameras = set(cameras)

    if angles is not None:
        angles = set(angles)

    for id_camera in images:

        if cameras is not None and id_camera not in cameras:
            continue

        for angle in images[id_camera]:

            if angles is not None and angle not in angles:
                continue

            yield id_camera, angle, images[id_camera][angle]


def as_image_views(images_iterator, calibration):
    """Convert an image iterator into a dictionary of ImageView objects.

    Args:
        images_iterator:
            Iterator yielding ``(camera_id, angle, image_array)`` tuples.
            Typically created with :func:`iter_images` or
            :func:`iter_image_paths`.
        calibration:
            Calibration object providing the method
            ``get_projection(camera_id, angle)``.

    Returns:
        Dictionary mapping ``"{camera_id}_{angle}"`` keys to
        :class:`ImageView` instances.

    Example:
        >>> iterator = iter_images(images)
        >>> image_views = as_image_views(iterator, calibration)
        >>> image_views["side_0"]
    """
    im_views = dict()
    for id_camera, angle, image in images_iterator:
        name = f'{id_camera}_{angle}'
        projection = calibration.get_projection(id_camera, angle)
        im_views[name] = ImageView(
            image,
            projection
        )
    return im_views

