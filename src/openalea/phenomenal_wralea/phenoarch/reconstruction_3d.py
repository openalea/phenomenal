from openalea.phenomenal.object import ImageView


def get_image_views(images_bin, calibration_side, calibration_top, ref_angle=None):
    # Select images
    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration_side.get_projection(angle)

        ref = False
        if angle == ref_angle:
            ref = True

        image_views.append(ImageView(images_bin['side'][angle], projection, inclusive=False, ref=ref))

    projection = calibration_top.get_projection(0)
    image_views.append(ImageView(images_bin['top'][0], projection, inclusive=True))

    return image_views
