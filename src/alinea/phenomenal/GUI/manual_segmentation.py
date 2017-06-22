#!/usr/bin/env python
from __future__ import print_function


import sys
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from alinea.phenomenal.data_structure import *
from alinea.phenomenal.segmentation_3d import *


def order_color_map():
    return [[0.99659628, 0.98889581, 0.16417371],
            [0.83230529, 0.00593472, 0.32600936],
            [0.9905601, 0.66138103, 0.65248322],
            [0.50300463, 0.35824967, 0.40976827],
            [0.20121525, 0.90008866, 0.88125667],
            [0.46160648, 0.18590851, 0.08820422],
            [0.0989774, 0.95619773, 0.5081731],
            [0.30118842, 0.77544763, 0.57621852],
            [0.41259761, 0.07674815, 0.18858604],
            [0.36514937, 0.60726936, 0.75827691],
            [0.49487075, 0.18661031, 0.64018052],
            [0.32736059, 0.63990736, 0.52639877],
            [0.73626298, 0.48061824, 0.42261254],
            [0.92210567, 0.33199288, 0.42462369],
            [0.01091914, 0.10072095, 0.60956167],
            [0.326969, 0.05678654, 0.42627795],
            [0.25886678, 0.70902097, 0.51379045],
            [0.5488322, 0.04307052, 0.15873569],
            [0.99267921, 0.4272508, 0.94135324],
            [0.3658708, 0.24918325, 0.09313606],
            [0.72872193, 0.32411031, 0.79628119],
            [0.7391597, 0.16755361, 0.84783927],
            [0.93533081, 0.1477583, 0.52533179],
            [0.19822189, 0.66249198, 0.69137387],
            [0.00507715, 0.97216072, 0.13574054],
            [0.11516606, 0.00247501, 0.21798785],
            [0.51077825, 0.88239746, 0.25077849],
            [0.92052319, 0.58308706, 0.82725008],
            [0.23451286, 0.26491946, 0.68560348],
            [0.03787533, 0.24459271, 0.01686671],
            [0.882183, 0.75517859, 0.26435312],
            [0.82714058, 0.33109862, 0.45433856],
            [0.69019816, 0.53812725, 0.91802668],
            [0.34458098, 0.28853241, 0.63736325],
            [0.65782353, 0.74088678, 0.02012788],
            [0.37853074, 0.81197471, 0.63751254],
            [0.73690095, 0.44390273, 0.19167143],
            [0.91811865, 0.25752368, 0.32221395],
            [0.25013469, 0.26803252, 0.48229518],
            [0.21198857, 0.40885046, 0.51970764],
            [0.8952603, 0.86769159, 0.30295505],
            [0.47986356, 0.29210024, 0.23814659],
            [0.50097001, 0.97069059, 0.41633548],
            [0.3683041, 0.31478484, 0.46126809],
            [0.15798675, 0.84515883, 0.250781],
            [0.88131227, 0.18359461, 0.94047761],
            [0.63398678, 0.8151208, 0.16386482],
            [0.37401865, 0.85129173, 0.74466164],
            [0.38023029, 0.79971272, 0.22897326],
            [0.38335029, 0.675665, 0.75964123],
            [0.5823218, 0.288478, 0.02608493],
            [0.58151453, 0.10569082, 0.86928919],
            [0.40048766, 0.24869623, 0.64766116],
            [0.22386007, 0.63371727, 0.76404276],
            [0.63786672, 0.38547319, 0.20651756],
            [0.06084577, 0.79676479, 0.35152952],
            [0.76394067, 0.01441786, 0.82938017],
            [0.32192799, 0.22521577, 0.39676531],
            [0.01472772, 0.00270723, 0.57250408],
            [0.5936998, 0.15854627, 0.26003789],
            [0.27877293, 0.14619729, 0.21395228],
            [0.91551909, 0.64480282, 0.90247188],
            [0.11092836, 0.00180252, 0.61870791],
            [0.9285638, 0.93687744, 0.50497465],
            [0.41352979, 0.05975143, 0.61774515],
            [0.71868377, 0.79960734, 0.97451708],
            [0.92910295, 0.28342546, 0.13464499],
            [0.94000784, 0.46681916, 0.79475854],
            [0.75087793, 0.49671276, 0.69827291],
            [0.47866469, 0.94760904, 0.90653672],
            [0.43450178, 0.6464352, 0.32567589],
            [0.02899201, 0.53926606, 0.97402085],
            [0.88262852, 0.80409816, 0.36159281],
            [0.65692886, 0.44243292, 0.4680599],
            [0.65825715, 0.37210827, 0.21883511],
            [0.44877054, 0.61493776, 0.38578463],
            [0.70550681, 0.68375443, 0.35470367],
            [0.07095519, 0.7132003, 0.56680742],
            [0.16899307, 0.06207157, 0.31723708],
            [0.25416233, 0.58311468, 0.79500568],
            [0.71229483, 0.74262304, 0.53342871],
            [0.94466089, 0.27742922, 0.08378722],
            [0.63801291, 0.41283919, 0.82371736],
            [0.2889267, 0.95967466, 0.49421928],
            [0.12792755, 0.18582789, 0.08190621],
            [0.15150344, 0.53426738, 0.51068004],
            [0.54352207, 0.18724756, 0.46418694],
            [0.710452, 0.45439598, 0.7250237],
            [0.4470509, 0.95920151, 0.80538078],
            [0.12016771, 0.38885597, 0.33627806],
            [0.48304043, 0.27412207, 0.07885398],
            [0.1889273, 0.04956961, 0.05929954],
            [0.53066577, 0.96040878, 0.60020187],
            [0.00619975, 0.59113537, 0.82476673],
            [0.53822879, 0.53336228, 0.58252774],
            [0.97970743, 0.28917651, 0.14177852],
            [0.44392905, 0.64876136, 0.14495674],
            [0.8321701, 0.87201181, 0.74350387],
            [0.43033237, 0.11796306, 0.99403712],
            [0.88950737, 0.67593679, 0.062654],
            [0.84871963, 0.19127809, 0.83522607],
            [0.28209975, 0.20285313, 0.63583885],
            [0.53067358, 0.73624566, 0.89314851],
            [0.02276315, 0.10111074, 0.18114278],
            [0.27197106, 0.24110763, 0.68347256],
            [0.2351836, 0.13934713, 0.7069774],
            [0.71038558, 0.49296881, 0.38317342],
            [0.22517316, 0.70731924, 0.62699041],
            [0.15766851, 0.83372654, 0.68681055],
            [0.55891389, 0.07565491, 0.65963329],
            [0.91883765, 0.59691326, 0.94281448],
            [0.48494875, 0.97387279, 0.96659851],
            [0.96144783, 0.59149405, 0.71615595],
            [0.41916555, 0.7437236, 0.70075373],
            [0.92758847, 0.42259917, 0.04145682],
            [0.75723718, 0.17971824, 0.46305421],
            [0.60367758, 0.03440915, 0.82614578],
            [0.11790148, 0.20307221, 0.23293247],
            [0.55064242, 0.13958623, 0.37447411],
            [0.76754983, 0.35100953, 0.88132942],
            [0.67488323, 0.54310955, 0.22733381],
            [0.78699687, 0.41587862, 0.9048356],
            [0.39370955, 0.48314287, 0.7597023],
            [0.81015467, 0.70215175, 0.44414641],
            [0.46092117, 0.80021441, 0.74140582],
            [0.14593862, 0.52740398, 0.41271234],
            [0.14815373, 0.46568431, 0.95372908],
            [0.24313222, 0.398265, 0.89126157],
            [0.50820012, 0.91478451, 0.27229336],
            [0.91572479, 0.55613609, 0.34947137],
            [0.02648434, 0.65580734, 0.30153774],
            [0.64077903, 0.57872143, 0.3964199],
            [0.86337986, 0.0076321, 0.27749796],
            [0.19608934, 0.65254639, 0.60566829],
            [0.81585373, 0.63794431, 0.47724807],
            [0.9359453, 0.51760575, 0.72872922],
            [0.03361752, 0.90925632, 0.01687948],
            [0.81015908, 0.2935618, 0.23616386],
            [0.36788354, 0.96949353, 0.67108438],
            [0.30831752, 0.03445725, 0.36334659],
            [0.98380374, 0.9520577, 0.19559478],
            [0.43501797, 0.34077535, 0.7841277],
            [0.00964311, 0.70220517, 0.9243851],
            [0.07969448, 0.33752396, 0.33330211],
            [0.36705557, 0.21431697, 0.80008569],
            [0.96625254, 0.73769347, 0.38213452],
            [0.42380264, 0.90877587, 0.2681354],
            [0.54618676, 0.34544534, 0.37545651],
            [0.77441852, 0.36853367, 0.12689134],
            [0.43159979, 0.01816662, 0.88037533],
            [0.66826974, 0.48549808, 0.2009812],
            [0.48991181, 0.5999078, 0.70252382],
            [0.91287807, 0.75083434, 0.29650189],
            [0.27633327, 0.01299607, 0.88584358],
            [0.40245931, 0.24793636, 0.39074716],
            [0.91799352, 0.97252288, 0.63315271],
            [0.07240262, 0.51253118, 0.39215861],
            [0.84138425, 0.2150941, 0.68597167],
            [0.55972073, 0.60871003, 0.88028987],
            [0.65430293, 0.10272306, 0.22428676],
            [0.57860792, 0.82561022, 0.27002428],
            [0.89302512, 0.2516268, 0.43780892],
            [0.95426509, 0.56549646, 0.78279791],
            [0.14532344, 0.49694678, 0.27684528],
            [0.61649481, 0.17076419, 0.4495171],
            [0.40749831, 0.69833072, 0.2881697],
            [0.55097732, 0.41337633, 0.76646182],
            [0.36521687, 0.42034175, 0.33333733],
            [0.39737892, 0.47715016, 0.55296622],
            [0.43975443, 0.89632915, 0.51913656],
            [0.19588498, 0.20719466, 0.42735635],
            [0.25116383, 0.2064736, 0.1861576],
            [0.66592958, 0.96587725, 0.03923333],
            [0.29504762, 0.2436488, 0.25785969],
            [0.20691745, 0.96436179, 0.09389655],
            [0.55110049, 0.64482053, 0.65032048],
            [0.19160823, 0.05055096, 0.36974211],
            [0.36415071, 0.09511094, 0.9187953],
            [0.70517421, 0.22846148, 0.47985604],
            [0.9405986, 0.61551714, 0.47626611],
            [0.06818107, 0.28483604, 0.50432778],
            [0.21730272, 0.21208169, 0.09242148],
            [0.66371616, 0.91388404, 0.52658124],
            [0.72774499, 0.35484501, 0.84737908],
            [0.26059034, 0.97175533, 0.07436808],
            [0.67094163, 0.89239625, 0.83360094],
            [0.10489339, 0.03057839, 0.96404112],
            [0.49842927, 0.16129156, 0.81428536],
            [0.45427831, 0.11494776, 0.44231558],
            [0.28083915, 0.53267452, 0.59542529],
            [0.58712758, 0.83134879, 0.78030605],
            [0.5964846, 0.84367842, 0.43467896],
            [0.3082119, 0.09722437, 0.38003406],
            [0.62351039, 0.30055298, 0.65344687],
            [0.26671144, 0.86402236, 0.09972766],
            [0.12078761, 0.19398046, 0.94205608],
            [0.30022481, 0.69857511, 0.7172752],
            [0.78933215, 0.64514183, 0.01292835],
            [0.29776719, 0.21929239, 0.36980935],
            [0.26128454, 0.40454539, 0.03730191],
            [0.5986524, 0.2887452, 0.18957669],
            [0.18877147, 0.66473875, 0.77111934],
            [0.30951933, 0.08958304, 0.89824029],
            [0.59409421, 0.66059752, 0.26274495],
            [0.79101634, 0.82926552, 0.30108431],
            [0.01805396, 0.26869938, 0.72515895],
            [0.4587787, 0.06378394, 0.06996459],
            [0.22953141, 0.92856963, 0.62436395],
            [0.50802725, 0.85119567, 0.88649199],
            [0.72243759, 0.26344264, 0.51961698],
            [0.73525254, 0.07440496, 0.5934549],
            [0.28604385, 0.85736956, 0.93027368],
            [0.61500943, 0.32376048, 0.38792129],
            [0.33369656, 0.15818153, 0.96512325],
            [0.06812052, 0.53285771, 0.08047602],
            [0.87508692, 0.07545116, 0.4504402],
            [0.85568132, 0.62908724, 0.86743762],
            [0.76269111, 0.94004838, 0.83072654],
            [0.59686772, 0.71849284, 0.55896133],
            [0.01057939, 0.67552542, 0.05224903],
            [0.05663043, 0.78106252, 0.88011577],
            [0.40241329, 0.3224162, 0.62379985],
            [0.17641979, 0.3100448, 0.85966449],
            [0.11639373, 0.43646362, 0.70915615],
            [0.55528813, 0.8644289, 0.21645791],
            [0.91827409, 0.23204106, 0.18565459],
            [0.19791603, 0.90860149, 0.84867205],
            [0.24030999, 0.5276062, 0.63276792],
            [0.85422985, 0.17308869, 0.30651335],
            [0.74057639, 0.1998055, 0.81616309],
            [0.91514573, 0.35691208, 0.36455314],
            [0.19425044, 0.28158583, 0.94452262],
            [0.21849039, 0.76363471, 0.73722863],
            [0.98022159, 0.03232114, 0.0381494],
            [0.52626537, 0.6015652, 0.87111255],
            [0.75484712, 0.84626045, 0.8859326],
            [0.66181195, 0.96041177, 0.98459778],
            [0.46996664, 0.03973603, 0.43935606],
            [0.83399453, 0.52283981, 0.42055007],
            [0.63299066, 0.09090263, 0.55637713],
            [0.30791476, 0.17809144, 0.92460965],
            [0.79913822, 0.5161944, 0.47832411],
            [0.91671869, 0.05145992, 0.59817817],
            [0.74461509, 0.68582085, 0.6039091],
            [0.98611966, 0.66824317, 0.7559762],
            [0.1996829, 0.33888566, 0.80898721],
            [0.20898959, 0.85739826, 0.28869989],
            [0.05152039, 0.52047787, 0.76018112],
            [0.09232488, 0.90074582, 0.95564026],
            [0.16697392, 0.43273632, 0.84981986],
            [0.48157259, 0.32689508, 0.89570153],
            [0.77718, 0.69346373, 0.38664724],
            [0.18161662, 0.74627374, 0.9018046],
            [0.33099297, 0.80525437, 0.7363759],
            [0.08612859, 0.24468667, 0.85253495],
            [0.34564459, 0.79338833, 0.30948505]]


def vtk_get_text_actor(text, position=(0, 0, 0), scale=5, color=(0, 0, 1)):

    textSource = vtk.vtkVectorText()
    textSource.SetText(text)
    textSource.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(textSource.GetOutputPort())

    actor = vtk.vtkFollower()
    actor.SetMapper(mapper)
    actor.SetScale(scale, scale, scale)
    actor.AddPosition(position[0], position[1], position[2])

    actor.GetProperty().SetColor(color[0], color[1], color[2])

    return actor


def vtk_get_ball_actor_from_position(position, radius=5, color=(1, 0, 0)):

    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(position[0], position[1], position[2])
    sphereSource.SetRadius(radius)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])

    return actor


def vtk_get_actor_from_voxels(voxels_position, voxels_size,
                              color=(0, 1, 0)):

    points = vtk.vtkPoints()
    for v in voxels_position:
        points.InsertNextPoint(v[0], v[1], v[2])

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    cubeSource = vtk.vtkCubeSource()
    cubeSource.SetXLength(voxels_size)
    cubeSource.SetYLength(voxels_size)
    cubeSource.SetZLength(voxels_size)

    glyph3D = vtk.vtkGlyph3D()

    if vtk.VTK_MAJOR_VERSION <= 5:
        glyph3D.SetSource(cubeSource.GetOutput())
        glyph3D.SetInput(polydata)
    else:
        glyph3D.SetSourceConnection(cubeSource.GetOutputPort())
        glyph3D.SetInputData(polydata)

    glyph3D.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])

    return actor


class MainWindow(QtGui.QMainWindow):

    def HLine(self):
        hline = QtGui.QFrame()
        hline.setFrameShape(QtGui.QFrame.HLine)
        hline.setFrameShadow(QtGui.QFrame.Sunken)
        return hline

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.main_frame = QtGui.QFrame()

        # ======================================================================

        self.init_segmentation_values()

        # ======================================================================
        # Define Widget

        self.button_openfilename = QtGui.QPushButton("Open")
        self.button_openfilename.clicked.connect(self.open_file)

        self.button_savefilename = QtGui.QPushButton("Save")
        self.button_savefilename.clicked.connect(self.save_file)

        self.cb_display_voxel = QtGui.QCheckBox("Display ALL Voxel")
        self.cb_display_voxel.setChecked(False)
        self.cb_display_voxel.stateChanged.connect(self.update_render)

        self.cb_display_voxel_leaf = QtGui.QCheckBox("Display Voxel Selected")
        self.cb_display_voxel_leaf.setChecked(False)
        self.cb_display_voxel_leaf.stateChanged.connect(self.update_render)

        self.cb_automatic_reorder = QtGui.QCheckBox("Automatic reorder")
        self.cb_automatic_reorder.setChecked(True)
        self.cb_automatic_reorder.stateChanged.connect(self.update_render)

        self.button_analysis = QtGui.QPushButton("Analysis")
        self.button_analysis.clicked.connect(self.analysis)

        self.label_last_mature_order = QtGui.QLabel('Last Mature Order')
        self.combo_last_mature_order = QtGui.QComboBox()
        self.combo_last_mature_order.addItems(map(str, range(1, 30, 1)))
        self.combo_last_mature_order.setCurrentIndex(0)

        self.label_label = QtGui.QLabel('Label')
        self.combo_label = QtGui.QComboBox()
        self.combo_label.addItems(self.labels)
        self.combo_label.currentIndexChanged.connect(
            self.combo_label_current_index_changed)
        self.combo_label.setCurrentIndex(0)

        self.cb_swap = QtGui.QCheckBox("Swap")
        self.cb_swap.setChecked(False)

        self.label_polyline = QtGui.QLabel('Polyline')
        self.combo_polyline = QtGui.QComboBox()
        self.combo_polyline.currentIndexChanged.connect(self.update_render)

        self.list_button = list()
        btn = QtGui.QPushButton("unknown")
        btn.clicked.connect(self.button_click)
        self.list_button.append(btn)

        btn = QtGui.QPushButton("stem")
        btn.clicked.connect(self.button_click)
        self.list_button.append(btn)

        for i in range(1, 31):
            btn = QtGui.QPushButton("leaf_" + str(i))
            btn.clicked.connect(self.button_click)
            self.list_button.append(btn)

        # ======================================================================
        # VTK RENDER

        self.ren = vtk.vtkRenderer()

        self.vtkWidget = QVTKRenderWindowInteractor(self.main_frame)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.camera = vtk.vtkCamera()
        self.camera.SetPosition(10, 10, 10)
        self.camera.SetFocalPoint(0, 0, 0)

        self.ren.SetActiveCamera(self.camera)
        self.ren.ResetCamera()
        self.ren.SetBackground(0.7, 0.7, 0.7)

        # ======================================================================
        # Organization of the Main Frame

        self.tools_layout = QtGui.QGridLayout()
        self.tools_layout.addWidget(self.button_openfilename, 0, 0)
        self.tools_layout.addWidget(self.button_savefilename, 0, 1)

        # Horizontal line separator
        self.tools_layout.addWidget(self.HLine(), 1, 0, 1, 2)

        self.tools_layout.addWidget(self.cb_display_voxel, 2, 0)
        self.tools_layout.addWidget(self.cb_display_voxel_leaf, 2, 1)

        self.tools_layout.addWidget(self.cb_automatic_reorder, 3, 0)

        self.tools_layout.addWidget(self.label_last_mature_order, 4, 0)
        self.tools_layout.addWidget(self.combo_last_mature_order, 4, 1)
        self.tools_layout.addWidget(self.button_analysis, 5, 1)

        self.tools_layout.addWidget(self.label_label, 6, 0)
        self.tools_layout.addWidget(self.combo_label, 6, 1)
        self.tools_layout.addWidget(self.cb_swap, 7, 1)

        self.tools_layout.addWidget(self.label_polyline, 8, 0)
        self.tools_layout.addWidget(self.combo_polyline, 8, 1)


        for i, btn in enumerate(self.list_button):
            self.tools_layout.addWidget(btn, 13 + i / 2, i % 2)

        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.tools_layout, stretch=20)
        self.main_layout.addWidget(self.vtkWidget, stretch=80)

        self.main_frame.setLayout(self.main_layout)
        self.setCentralWidget(self.main_frame)

        # ======================================================================
        self.show()
        self.iren.Initialize()

    def get_color(self, label, info):

        if label == "stem":
            return (0.5, 0.5, 0.5)
        elif label == "unknown":
            return (1, 1, 1)
        else:
            color_map = order_color_map()

            return color_map[info['order']]

    def init_segmentation_values(self):

        self.voxels_size = 0
        self.ball_radius = 0

        self.leaf_labels = ['leaf_' + str(i) for i in range(1, 31)]
        self.labels = ['unknown', 'stem'] + self.leaf_labels
        self.dict_vo_by_label = dict()

        for i, label in enumerate(self.labels):
            vo = VoxelOrgan(label)
            vo.info['voxels_size'] = self.voxels_size
            if i > 1:
                vo.info['order'] = i - 1

            vo.actor_color = self.get_color(vo.label, vo.info)
            self.dict_vo_by_label[label] = vo

            vo.actor_position_tip = None
            vo.actor_position_base = None
            vo.text_actor = None

    def update_render(self):

        current_text = str(self.combo_label.currentText())
        i = self.combo_polyline.currentIndex()

        for label in self.dict_vo_by_label:
            vo = self.dict_vo_by_label[label]

            for j, vs in enumerate(vo.voxel_segments):
                r, g, b = vo.actor_color
                vs.actor_voxels.GetProperty().SetColor(r, g, b)
                b = self.cb_display_voxel.isChecked()
                vs.actor_voxels.SetVisibility(b)

                if label == current_text:
                    b = self.cb_display_voxel_leaf.isChecked()
                    vs.actor_voxels.SetVisibility(b)

                    if i == j:
                        vs.actor_polyline.GetProperty().SetColor(1, 0, 0)
                    else:
                        vs.actor_polyline.GetProperty().SetColor(0, 0, 1)
                else:
                    vs.actor_polyline.GetProperty().SetColor(0, 0, 0)

            self.ren.RemoveActor(vo.actor_position_tip)
            self.ren.RemoveActor(vo.actor_position_base)
            self.ren.RemoveActor(vo.text_actor)

            if (label != "unknown" and len(vo.voxel_segments) > 0 and
                    "position_tip" in vo.info):

                vo.actor_position_tip = vtk_get_ball_actor_from_position(
                    vo.info['position_tip'],
                    radius=10,
                    color=(1, 0, 0))
                self.ren.AddActor(vo.actor_position_tip)

                vo.actor_position_base = vtk_get_ball_actor_from_position(
                    vo.info['position_base'],
                    radius=10,
                    color=(0, 0, 1))

                self.ren.AddActor(vo.actor_position_base)

                r, g, b = (0, 0, 1)
                if label == current_text:
                    r, g, b = (1, 0, 0)

                pos = vo.info['position_tip']
                pos = (pos[0] - 10, pos[1] - 10, pos[2])
                vo.text_actor = vtk_get_text_actor(
                    label,
                    position=pos,
                    scale=40,
                    color=(r, g, b))

                self.ren.AddActor(vo.text_actor)

                vo.text_actor.SetCamera(self.ren.GetActiveCamera())

        self.iren.Render()

    def render_voxel_maize_segmentation(self):

        self.ren.RemoveAllViewProps()
        self.iren.Render()

        for vo in self.dict_vo_by_label.values():
            for vs in vo.voxel_segments:
                vs.actor_voxels = vtk_get_actor_from_voxels(
                    vs.voxels_position,
                    self.voxels_size * 0.50,
                    color=vo.actor_color)
                self.ren.AddActor(vs.actor_voxels)

        for vo in self.dict_vo_by_label.values():
            for vs in vo.voxel_segments:
                vs.actor_polyline = vtk_get_actor_from_voxels(
                    vs.polyline,
                    self.voxels_size * 1,
                    color=(0, 0, 0))
                self.ren.AddActor(vs.actor_polyline)

        self.ren.ResetCamera()
        self.update_render()

    # ==========================================================================

    def get_vo_label(self, vo):
        if vo.label == "stem" or vo.label == "unknown":
            return vo.label
        else:
            return "leaf_" + str(vo.info['order'])

    def open_file(self):
        qfile_dialog = QtGui.QFileDialog()
        filename = qfile_dialog.getOpenFileName()
        if filename:
            self.init_segmentation_values()

            vms = VoxelMaizeSegmentation.read_from_json(filename)
            self.voxels_size = vms.voxels_size
            self.ball_radius = vms.ball_radius
            for vo in vms.voxel_organs:
                vo.actor_color = self.get_color(vo.label, vo.info)
                vo.actor_position_tip = None
                vo.actor_position_base = None
                vo.text_actor = None

                self.dict_vo_by_label[self.get_vo_label(vo)] = vo

            # self.initialize_manual_segmentation()
            self.render_voxel_maize_segmentation()
            self.combo_label_current_index_changed()

    def save_file(self):

        qfile_dialog = QtGui.QFileDialog()
        filename = str(qfile_dialog.getSaveFileName())

        if filename:
            vms = VoxelMaizeSegmentation(self.voxels_size, self.ball_radius)
            for label in self.dict_vo_by_label:

                vo = self.dict_vo_by_label[label]

                if len(vo.voxel_segments) > 0:
                    vms.voxel_organs.append(vo)
            vms.write_to_json(filename)

    # ==========================================================================
    # ==========================================================================

    def swap_organ(self, vo1, vo2):

        tmp_label = vo1.label
        tmp_info = vo1.info
        tmp_voxel_segments = vo1.voxel_segments
        tmp_order_1 = vo1.info['order']
        tmp_order_2 = vo2.info['order']

        vo1.label = vo2.label
        vo1.info = vo2.info
        vo1.voxel_segments = vo2.voxel_segments
        vo1.info['order'] = tmp_order_1

        vo2.label = tmp_label
        vo2.info = tmp_info
        vo2.voxel_segments = tmp_voxel_segments
        vo2.info['order'] = tmp_order_2

    def update_vo_global_order(self):

        for i in range(1, 31):
            vo1 = self.dict_vo_by_label['leaf_' + str(i)]
            if len(vo1.voxel_segments) == 0 and i < 30:
                vo2 = self.dict_vo_by_label['leaf_' + str(i + 1)]

                self.swap_organ(vo1, vo2)

    def analysis(self):

        last_mature = self.combo_last_mature_order.currentIndex() + 1
        vo_stem = self.dict_vo_by_label['stem']

        vo_stem_dst = maize_stem_analysis(vo_stem)
        vo_stem.info.update(vo_stem_dst.info)

        voxels = set(vo_stem.voxels_position())
        for i in range(1, 31):

            vo = self.dict_vo_by_label['leaf_' + str(i)]

            if vo.info['order'] > last_mature:
                vo_dst = maize_cornet_leaf_analysis(
                    vo, vo_stem.info['vector_mean'], voxels)
            else:
                vo_dst = maize_mature_leaf_analysis(
                    vo, vo_stem.info['vector_mean'])

            voxels = voxels.union(set(vo_dst.voxels_position()))
            vo.info.update(vo_dst.info)

        self.update_render()

    # def update_vo(self, vo):
    #
    #     last_mature = self.combo_last_mature_order.currentIndex() + 1
    #
    #     if vo.label == 'unknown' or vo == "stem":
    #         return vo
    #
    #     order = vo.info['order']
    #
    #     vo_stem = self.dict_vo_by_label['stem']
    #     if order > last_mature:
    #         voxels = set(vo_stem.voxels_position())
    #         for i in range(1, order):
    #             vo_i = self.dict_vo_by_label['leaf_' + str(i)]
    #             voxels = voxels.union(set(vo_i.voxels_position()))
    #
    #         vo_dst = maize_cornet_leaf_analysis(
    #             vo, vo_stem.info['vector_mean'], voxels)
    #     else:
    #
    #         vo_dst = maize_mature_leaf_analysis(
    #             vo, vo_stem.info['vector_mean'])
    #
    #     vo.info.update(vo_dst.info)

    def button_click(self):

        current_text = str(self.combo_label.currentText())
        vo_selected = self.dict_vo_by_label[current_text]

        current_text = str(self.sender().text())
        vo_dest = self.dict_vo_by_label[current_text]

        if self.cb_swap.isChecked():
            self.swap_organ(vo_selected, vo_dest)
        else:
            i = self.combo_polyline.currentIndex()
            vs = vo_selected.voxel_segments[i]

            vo_selected.voxel_segments.remove(vs)
            vo_dest.voxel_segments.append(vs)

            self.combo_polyline.removeItem(i)
            self.combo_polyline.setCurrentIndex(max(0, i - 1))

            if self.cb_automatic_reorder.isChecked():
                self.update_vo_global_order()
            # self.update_vo(vo_selected)
            # self.update_vo(vo_dest)

        self.update_render()

    def combo_label_current_index_changed(self):

        current_text = str(self.combo_label.currentText())

        self.combo_polyline.clear()
        vo_selected = self.dict_vo_by_label[current_text]
        for i, vs in enumerate(vo_selected.voxel_segments):
            self.combo_polyline.addItem("Polyline {}".format(i + 1))

        self.update_render()

    # ==========================================================================
    # ==========================================================================


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())