import cv2
import pytest

import openalea.phenomenal.display as phm_display

from pathlib import Path
HERE = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
DATADIR = HERE.parent / "data" / "plant_1"


@pytest.mark.skip()
def test_display_image():
    img = cv2.imread(DATADIR / "bin" / "side" / "0.png")
    img_col = cv2.imread(DATADIR / "raw" / "side" / "0.png")
    phm_display.show_image(img)
    phm_display.show_image(img_col)
    phm_display.show_images([img, img_col])
