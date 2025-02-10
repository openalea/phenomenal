import os
import cv2
import pytest

import openalea.phenomenal.display as phm_display

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data")


@pytest.mark.skip()
def test_display_image():
    img = cv2.imread(os.path.join(dir_path, "plant_1", "bin", "side", "0.png"))
    img_col = cv2.imread(os.path.join(dir_path, "plant_1", "raw", "side", "0.jpg"))
    phm_display.show_image(img)
    phm_display.show_image(img_col)
    phm_display.show_images([img, img_col])
