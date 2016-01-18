# -*- python -*-
# -*- coding:utf-8 -*-
#
#       configuration.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os
import glob
# ==============================================================================


def import_images(image_directory, genotype_name, plant_id):
    """
    Return a dictionary of side images according to the structure of
    image_directory.

    key is a date
    value is a list of path images

    Structure required :
        image_directory/genotype_name/plant_id*sv*.png

    :param image_directory: The root image directory
    :param genotype_name: String of genotype name
    :param plant_id: String of id of plant
    :return:Dict dates: image for the images matching plant_id in the
    genotype image collection
    """

    im_dir = os.path.join(image_directory, genotype_name, plant_id)
    side_views = glob.glob(im_dir + '*sv*.png')
    dates = map(lambda s: os.path.basename(s).split(' ')[0].split('_')[-1],
                side_views)
    images = {d: [] for d in set(dates)}
    for i, d in enumerate(dates):
        images[d].append(side_views[i])

    return images
