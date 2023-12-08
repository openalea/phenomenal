"""Test computation used in calibration tutorial (examples/calibration)"""

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.calibration as phm_calib


def test_detect_corners():
    chessboard_images = phm_data.chessboard_images("data/plant_1")[0]
    square_size_of_chessboard = 47  # In mm
    square_shape_of_chessboard = (8, 6)  # (8 square x 6 square on chessboard)
    chessboard = phm_calib.Chessboard(square_size_of_chessboard,
                                      square_shape_of_chessboard)
    for id_camera in chessboard_images:
        for angle in chessboard_images[id_camera]:
            im = chessboard_images[id_camera][angle]
            found = chessboard.detect_corners(id_camera, angle, im, check_order=False)
            assert found
    assert 'side' in chessboard.image_points
    assert len(chessboard.image_points['side'][42]) == 48


def test_calibrate():
    image_points = phm_data.image_points("data/plant_1")
    calibrator = phm_calib.Calibrator(south_camera=('side', 90, 5500),
                            targets={'target_1': (45, 48), 'target_2': (45, 48 + 180)},
                            chessboards={'target_1': (47, 8, 6),
                                         'target_2': (47, 8, 6)})
    calibrator.load_image_points(image_points)
    calibration = calibrator.calibrate()
    assert 'side' in calibration._cameras
    assert(round(calibration.calibration_statistics['mean_error'], 2)) == 0.24