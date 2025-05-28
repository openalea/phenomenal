import cv2
import pytest
import os

import openalea.phenomenal.display as phm_display

from pathlib import Path
test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir.parent / "data" / "plant_1"


@pytest.mark.skpif(os.getenv("CI") == "true", reason="Skipped in CI environments")
def test_display_image():
    img = cv2.imread(data_dir / "bin" / "side" / "0.png")
    img_col = cv2.imread(data_dir / "chessboard" / "side" / "42.jpg")
    phm_display.show_image(img)
    phm_display.show_image(img_col)
    phm_display.show_images([img, img_col])
