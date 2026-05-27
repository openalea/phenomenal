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
    def __init__(self, image, projection):
        self.image = image
        self.projection = projection
        self.integral = None


def get_image_views(image_paths, calibration, imread):
    im_views = dict()
    for id_camera in image_paths:
        for angle in image_paths[id_camera]:
            name = f'{id_camera}_{angle}'
            projection = calibration.get_projection(id_camera, angle)
            im_views[name] = ImageView(
                imread(image_paths[id_camera][angle]),
                projection
            )
    return im_views