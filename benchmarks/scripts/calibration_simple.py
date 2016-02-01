# -*- python -*-
#
#       calibration.py : 
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
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
import alinea.phenomenal.plant_1
import alinea.phenomenal.chessboard
import alinea.phenomenal.calibration_top
# ==============================================================================

chessboards_path = alinea.phenomenal.plant_1.plant_1_chessboards_path()

# Load Chessboard
chessboard_1 = alinea.phenomenal.chessboard.Chessboard.read(chessboards_path[0])
chessboard_2 = alinea.phenomenal.chessboard.Chessboard.read(chessboards_path[1])

# ==============================================================================
# Calibration

# Create Object
calibration = alinea.phenomenal.calibration_top.Calibration(
    chessboard_1, (2056, 2454), verbose=True)

# Do Calibration
guess = calibration.find_model_parameters(
    number_of_repetition=5)

# ==============================================================================
# Print parameters

print guess