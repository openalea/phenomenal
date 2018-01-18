from openalea.phenomenal.data import plant_1_images


def plant_images_split():
    """Get the images data and return it in 2 separate dict
    """

    raw_images = plant_1_images()
    return raw_images['top'].values(), raw_images['side'].values()


