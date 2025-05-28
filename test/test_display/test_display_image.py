import pytest
from pathlib import Path
import openalea.phenomenal.display as phm_display
from openalea.phenomenal.image.io import read_image


@pytest.fixture
def matplotlib():
    return pytest.importorskip("matplotlib")


@pytest.fixture
def data_dir():
    test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
    data_dir = test_subdir.parent / "data" / "plant_1"
    return data_dir


def test_display_image(matplotlib, data_dir):
    img = read_image(data_dir / "bin" / "side" / "0.png", 'L')
    img_col = read_image(data_dir / "chessboard" / "side" / "42.jpg", 'RGB')
    phm_display.show_image(img)
    phm_display.show_image(img_col)
    phm_display.show_images([img, img_col])
