# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import numpy
import openalea.phenomenal.calibration as phm_calib
import openalea.phenomenal.data as phm_data

from pathlib import Path
HERE = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
DATADIR = HERE.parent / "data" / "plant_1"
# ==============================================================================

lemnatec2 = {
    "angle_factor": 1.000196048985029,
    "cameras_parameters": {
        "side": {
            "_focal_length_x": 4673.858469128553,
            "_focal_length_y": 4671.176406737264,
            "_height_image": 2454,
            "_pos_x": 7.416535279860737,
            "_pos_y": -5446.349857591031,
            "_pos_z": 0.0,
            "_rot_x": -1.563436412611411,
            "_rot_y": -0.0034441048748163894,
            "_rot_z": -0.0013892635134205022,
            "_width_image": 2056,
        },
        "top": {
            "_focal_length_x": 3786.9976615441783,
            "_focal_length_y": 3774.298507266704,
            "_height_image": 2056,
            "_pos_x": 13.351850903226996,
            "_pos_y": 2.2518764959739954,
            "_pos_z": 2661.0739077404382,
            "_rot_x": 3.140604378068007,
            "_rot_y": 0.0013393974482163173,
            "_rot_z": 0.003890406092895482,
            "_width_image": 2454,
        },
    },
    "clockwise": True,
    "reference_camera": "side",
    "targets_parameters": {
        "target_1": {
            "_pos_x": 173.8113353568984,
            "_pos_y": -117.1160724826211,
            "_pos_z": 289.41396894009847,
            "_rot_x": 1.322954720666246,
            "_rot_y": 0.03259785478254251,
            "_rot_z": 0.8717478672441068,
        },
        "target_2": {
            "_pos_x": -158.92264324949636,
            "_pos_y": 142.91039605963402,
            "_pos_z": 263.4924154812679,
            "_rot_x": 1.2812023189269341,
            "_rot_y": -0.045830612887471034,
            "_rot_z": -2.3541476545144135,
        },
    },
}


def test_calibration_working():
    chess = phm_data.chessboards(DATADIR)
    assert len(chess) == 2

def test_find_points():
    pass
    # image_points = {'side': [(478, 1969), (1550, 1976)],
    #                 'top': [(473, 255), (1951, 258)]}
    # # accelerate test
    # guess = [(700, 700, -700), (-700, 700, -700)]
    # calib = phm_calib.Calibration.from_dict(lemnatec2)
    # pts = calib.find_points(image_points, guess, niter=2)
    # expected = [[-710.670687,  732.762684, -936.617387],
    #             [694.774179,  736.698475, -945.038652]]
    # numpy.testing.assert_allclose(pts, expected, atol=1e-2)


def test_find_frame():
    image_points = {
        "side": [(478, 1969), (1550, 1976), (1250, 2193), (776, 2191)],
        "top": [(473, 255), (1951, 258), (1460, 1799), (958, 1798)],
    }
    calib = phm_calib.Calibration.from_dict(lemnatec2)
    fr, fpts = calib.find_frame(
        image_points,
        [("x", "y", 0) for _ in image_points["side"]],
        fixed_parameters={"_pos_x": 0, "_pos_y": 0},
    )
    numpy.testing.assert_almost_equal(fr._pos_z, -938.86, decimal=2)
    expected = [
        (-710.748065, 732.711416, 0),
        (694.650717, 736.685707, 0),
        (232.955844, -735.798007, 0),
        (-244.093682, -736.321985, 0),
    ]
    numpy.testing.assert_allclose(fpts, expected, rtol=0.01)


def test_find_camera():
    pass
    # image_points = [(483, 248), (1972, 242), (1487, 1796), (982, 1798)]
    # target_points = [[-710.69782628, 732.79049079, -936.7542377],
    #                  [694.68805505, 736.60566056, -944.58282677],
    #                  [232.88649682, -735.81085532, -938.29077936],
    #                  [-244.15336169, -736.29942847, -935.63550613]]
    # image_size = (2454, 2056)
    # calib = phm_calib.Calibration.from_dict(lemnatec2)
    # fx, fy = calib._cameras['top'].get_intrinsic()[numpy.diag_indices(2)]
    # camera = calib.find_camera(image_points, target_points, image_size,
    #                            fixed_parameters={'_focal_length_x': fx,
    #                                              '_focal_length_y': fy},
    #                            guess=calib._cameras['top'])
    # numpy.testing.assert_almost_equal(camera._pos_x, -10.49, decimal=2)
    # numpy.testing.assert_almost_equal(camera._pos_y, 10.07, decimal=2)
    # numpy.testing.assert_almost_equal(camera._focal_length_x, fx, decimal=2)
