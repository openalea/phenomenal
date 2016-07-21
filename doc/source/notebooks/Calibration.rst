
Calibration
===========

1. Prerequisites
----------------

1.1 Chessboard object
~~~~~~~~~~~~~~~~~~~~~

See Chessboard notebook to create one chessboard object if he don't
exist or load existing file with :

.. code:: python

    from alinea.phenomenal.data_access.plant_1 import plant_1_chessboards
    
    # Load chessboard object
    chess_1, chess_2 = plant_1_chessboards()

2. Calibrate
------------

2.1 Do calibration
~~~~~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.calibration import (
        CalibrationCameraSideWith2TargetYXZ)
    
    # Define size image of image chessboard to calibrate
    size_image = (2056, 2454)
    
    # Calibrate
    id_camera = "side"
    calibration = CalibrationCameraSideWith2TargetYXZ()
    err = calibration.calibrate(chess_1.get_corners_2d(id_camera), 
                                chess_1.get_corners_local_3d(),
                                chess_2.get_corners_2d(id_camera), 
                                chess_2.get_corners_local_3d(),
                                size_image,
                                number_of_repetition=5)
    
    print err

2.2 Dump & load
~~~~~~~~~~~~~~~

.. code:: python

    # Dump
    calibration.dump('calibration_camera_side')

.. code:: python

    from alinea.phenomenal.calibration.calibration import CalibrationCameraSideWith2Target
    
    # Load 
    calibration = CalibrationCameraSideWith2Target.load('calibration_camera_side')
    
    print calibration

2.6 Viewing calibration result
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.6.1 Download dataset examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the chessboard image dataset
`here <https://gforge.inria.fr/frs/download.php/file/35019/CHESSBOARD_PhenoArch_2013_sv_face1.zip>`__
and extract it. Indicate the path in **data\_path\_directory** variable
below.

.. code:: python

    data_path_directory = './CHESSBOARD_PhenoArch_2013_sv_face1/'

2.6.1 Load path file from chessboard image dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import glob
    
    # Load path files from directory
    files_path = glob.glob(data_path_directory + '*.png')
    
    # Extract angles from path files
    angles = map(lambda x: int((x.split('_sv')[-1]).split('.png')[0]), files_path)
    
    images_path = dict()
    for i in range(len(files_path)):
        images_path[angles[i]] = files_path[i]

2.6.2 Show chessboard image with corners projection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    %matplotlib notebook
    
    import matplotlib.pyplot
    
    import cv2
    # from alinea.phenomenal.display.image import 
    
    angle = 42
    img = cv2.imread(images_path[angle], cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # BLUE POINTS ARE POINTS POSITIONS DETECTED BY OPENCV CHESSBOARD DETECTION 
    pt_2d = chess_1.image_points["side"][angle].astype(int)
    img[pt_2d[:, 0, 1], pt_2d[:, 0, 0]] = [0, 0, 255]
    
    # RED POINTS ARE POINTS POSITIONS PROJECTED BY CALIBRATION CHESSBOARD COMPUTATION
    points_2d = calibration.get_target_1_projected(angle, chess_1.get_corners_local_3d())
    for x, y in points_2d:
        img[int(y), int(x)] = [255, 0, 0]
    
    
    matplotlib.pyplot.figure()
    matplotlib.pyplot.imshow(img)

