import pytest
import os
import sys
from pathlib import Path
import openalea.phenomenal.display as phm_display
from openalea.phenomenal.image.io import read_image

skip_on_ci_non_linux = pytest.mark.skipif(
    os.environ.get("CI") == "true" and not sys.platform.startswith("linux"),
    reason="Skipped on CI except on Linux"
)

@pytest.fixture
def matplotlib():
    return pytest.importorskip("matplotlib")


@pytest.fixture
def data_dir():
    test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
    data_dir = test_subdir.parent / "data" / "plant_1"
    return data_dir


@skip_on_ci_non_linux
def test_display_image(matplotlib, data_dir):
    img = read_image(data_dir / "bin" / "side" / "0.png", 'L')
    img_col = read_image(data_dir / "chessboard" / "side" / "42.jpg", 'RGB')
    phm_display.show_image(img)
    phm_display.show_image(img_col)
    phm_display.show_images([img, img_col])
