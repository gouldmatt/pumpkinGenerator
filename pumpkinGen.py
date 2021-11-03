"""
Script generates pumpkins with randomized features 
"""

import sys
import random

from PySide2.QtWidgets import QSlider

from PySide2 import QtCore
from PySide2 import QtWidgets
# from maya.cmds.Modeling import constructionHistory
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()

    # to support older versions of python
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class PumpkinCreateDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(PumpkinCreateDialog, self).__init__(parent)

        self.setWindowTitle("Create Pumpkins")
        self.setMinimumWidth(200)

        # Remove the ? from the dialog on Windows
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.num_pumpkins = 0

    def create_slider(self):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(1, 64)
        slider.setPageStep(1)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        return(slider)

    def create_widgets(self):
        self.slider_num_pumpkins = self.create_slider()
        self.number_display = QtWidgets.QLabel("0")
        self.create_btn = QtWidgets.QPushButton("Create Pumpkin")

    def create_layouts(self):
        horz_layout = QtWidgets.QHBoxLayout()
        horz_layout.addWidget(self.slider_num_pumpkins)
        horz_layout.addWidget(self.number_display)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(horz_layout)
        main_layout.addWidget(self.create_btn)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_pumpkin)
        self.slider_num_pumpkins.valueChanged.connect(self.number_changed)

    def number_changed(self, value):
        self.number_display.setText(str(value))
        self.num_pumpkins = int(value)

    def create_pumpkin(self):
        j = 0
        k = 0
        for i in range(self.num_pumpkins):
            self.create_single_pumpkin()
            cmds.move(0, j*2, k*2)
            k = k + 1

            if i % 3 == 0 and i != 0:
                j = j + 1
                k = 0

        myBlinn = cmds.shadingNode('blinn', asShader=True, n="pumpkinMaterial")
        cmds.setAttr("pumpkinMaterial.color", 0.5783,
                     0.3092, 0.102, type='double3')
        for i in range(self.num_pumpkins):
            cmds.select("pumpkin" + str(i+1) + "|pumpkin")
            cmds.hyperShade(assign=myBlinn)

    def create_single_pumpkin(self):
        self.create_main_pumpkin()
        self.create_stems()
        cmds.group(em=True, name='pumpkin_cuts')
        self.create_eyes()
        self.create_nose()
        self.create_mouth()

        # cmds.select(clear=True)
        # cmds.select(all=True)
        # cmds.select(self.pumpkin_name, deselect=True)
        # cmds.select(self.pumpkin_name +'_stem', deselect=True)
        # cmds.select(self.pumpkin_name + '_bottom_stem', deselect=True)
        # cut_names = cmds.ls('cut*', sl=True)
        # cmds.select(cut_names)

        cmds.select(self.pumpkin_name)
        cmds.polyRemesh(maxEdgeLength=0.6,
                        collapseThreshold=0.5, smoothStrength=100)
        cmds.rename('pumpkin_before')

        cmds.polyCBoolOp('pumpkin_before', 'pumpkin_cuts',
                         op=2, cls=2, n=self.pumpkin_name)

        cmds.select(self.pumpkin_name)
        cmds.delete(ch=True)

        cmds.pointLight(rgb=[1.00, 0.51, 0.18], i=5,
                        n=self.pumpkin_name+"_point_light")

        cmds.group(self.pumpkin_name, self.pumpkin_name +
                   "_stem", self.pumpkin_name+"_bottom_stem", self.pumpkin_name+"_point_light", n=self.pumpkin_name)

    def create_main_pumpkin(self):
        cmds.polySphere(n="pumpkin", sh=11, sa=11)
        self.pumpkin_name = cmds.ls(sl=True)[0]
        cmds.scale(1, 0.8, 1)
        cmds.polyMoveVertex(self.pumpkin_name + '.vtx[110]',
                            self.pumpkin_name + '.vtx[0:21]', s=(1, 0.93, 1))

        cmds.polyMoveVertex(self.pumpkin_name + '.vtx[88:109]',
                            self.pumpkin_name + '.vtx[111]', s=(1, 0.93, 1))

        cmds.select(clear=True)

        cmds.softSelect(sse=1, ssd=0.53, sud=0.5)
        cmds.select(self.pumpkin_name + ".vtx[111]")
        cmds.move(0, -0.5, 0, os=True, wd=True, r=True)

        cmds.select(self.pumpkin_name + ".vtx[110]")
        cmds.move(0, 0.3, 0, os=True, wd=True, r=True)

        cmds.softSelect(sse=0)

        cmds.select(self.pumpkin_name)

        for i in range(220, 231):
            cmds.polySelect(el=i)
            edgeLoop = cmds.ls(sl=True)
            cmds.polyDuplicateEdge(edgeLoop, of=0.1)

        for i in range(220, 231):
            cmds.polySelect(el=i, add=True)

        cmds.scale(0.9, 0.9, 0.9)

        cmds.polySmooth(self.pumpkin_name, dv=1, c=1)

        cmds.select(self.pumpkin_name)
        cmds.polyExtrudeFacet(ltz=0.04)
        cmds.select(self.pumpkin_name)

    def create_eyes(self):
        self.left_eye_y = random.uniform(0.8, 0.9)
        self.left_eye_z = random.uniform(0, 0.3)
        self.right_eye_y = random.uniform(0.8, 0.9)
        self.right_eye_z = random.uniform(0.7, 1)
        shape = random.sample(['circle', 'diamond', 'triangle'], 1)

        if shape == ['circle']:
            self.make_pumpkin_circle_cut(
                self.left_eye_y, self.left_eye_z, 2, 2, '0deg')
            self.make_pumpkin_circle_cut(
                self.right_eye_y, self.right_eye_z, 2.5, 2, '0deg')
        elif shape == ['diamond']:
            self.make_pumpkin_rectangle_cut(
                self.left_eye_y, self.left_eye_z, 2, 2.5, '45deg')
            self.make_pumpkin_rectangle_cut(
                self.right_eye_y, self.right_eye_z, 2, 2.5, '45deg')
        else:
            self.make_pumpkin_triangle_cut(
                self.left_eye_y, self.left_eye_z, 2, 2.5, '0deg')
            self.make_pumpkin_triangle_cut(
                self.right_eye_y, self.right_eye_z, 2, 2.5, '0deg')

        left_eyebrow_y = self.left_eye_y + random.uniform(0.17, 0.2)
        left_eyebrow_z = self.left_eye_z + random.uniform(-0.05, 0.08)
        right_eyebrow_y = self.right_eye_y + random.uniform(0.17, 0.2)
        right_eyebrow_z = self.right_eye_z + random.uniform(-0.05, 0.08)

        shape = random.sample(['circle', 'diamond', 'triangle'], 1)
        eyebrow_angle = random.uniform(0, 45)

        if shape == ['circle']:
            self.make_pumpkin_circle_cut(
                left_eyebrow_y, left_eyebrow_z, 0.5, 2, str(-eyebrow_angle) + 'deg')
            self.make_pumpkin_circle_cut(
                right_eyebrow_y, right_eyebrow_z, 0.5, 2, str(eyebrow_angle) + 'deg')
        elif shape == ['diamond']:
            self.make_pumpkin_rectangle_cut(
                left_eyebrow_y, left_eyebrow_z, 0.5, 2, str(-eyebrow_angle) + 'deg')
            self.make_pumpkin_rectangle_cut(
                right_eyebrow_y, right_eyebrow_z, 0.5, 2, str(eyebrow_angle) + 'deg')
        else:
            self.make_pumpkin_triangle_cut(
                left_eyebrow_y, left_eyebrow_z, 0.5, 2, str(eyebrow_angle) + 'deg')
            self.make_pumpkin_triangle_cut(
                right_eyebrow_y, right_eyebrow_z, 0.5, 2, str(-eyebrow_angle) + 'deg')

    def create_nose(self):
        near_center_y = random.uniform(0.5, 0.75)
        near_center_z = (self.left_eye_z + self.right_eye_z)/2
        shape = random.sample(['circle', 'diamond', 'triangle'], 1)

        if shape == ['circle']:
            self.make_pumpkin_circle_cut(
                near_center_y, near_center_z, 2.5, 2, '0deg')
        elif shape == ['diamond']:
            self.make_pumpkin_rectangle_cut(
                near_center_y, near_center_z, 2, 2.5, '0deg')
        else:
            self.make_pumpkin_triangle_cut(
                near_center_y, near_center_z, 2, 2.5, '0deg')

    def create_mouth(self):
        shape = random.sample(['happy', 'sad', 'neutral'], 1)

        mouth_baseline = random.uniform(0, 0.1)
        mouth_top = random.uniform(mouth_baseline, 0.45)

        self.make_pumpkin_triangle_cut(mouth_top, 0, 3, 1, '45deg')
        self.make_pumpkin_rectangle_cut(mouth_baseline + 0.5 *
                                        (mouth_top-mouth_baseline), 0.1, 1.5, 1.5, '45deg')
        self.make_pumpkin_rectangle_cut(mouth_baseline, 0.3, 1.5, 1.5, '45deg')
        self.make_pumpkin_rectangle_cut(mouth_baseline, 0.5, 1.5, 1.5, '45deg')
        self.make_pumpkin_rectangle_cut(mouth_baseline, 0.7, 1.5, 1.5, '45deg')
        self.make_pumpkin_rectangle_cut(mouth_baseline + 0.5 *
                                        (mouth_top-mouth_baseline), 0.9, 1.5, 1.5, '45deg')
        self.make_pumpkin_triangle_cut(mouth_top, 1, 3, 1, '-45deg')

    def create_stems(self):
        cmds.polyCylinder(name=self.pumpkin_name + "_stem", height=3,
                          subdivisionsAxis=10, subdivisionsHeight=2)
        cmds.scale(0.12, 0.12, 0.12)
        cmds.move(0, 0.65, 0)

        cmds.polySelect(el=10)
        cmds.move(0, -0.07, 0, os=True, wd=True, r=True)

        cmds.select(self.pumpkin_name + "_stem" + ".e[0:9]")
        cmds.scale(1.5, 1.5, 1.5)

        cmds.select(self.pumpkin_name + "_stem" + ".f[21]")

        cmds.rotate('45deg', 0, 0, r=True)

        cmds.select(self.pumpkin_name + "_stem" + ".e[0:9]")
        cmds.polyCrease(value=10)

        cmds.select(self.pumpkin_name + "_stem" + ".e[20:29]")
        cmds.polyCrease(value=0.5)

        cmds.polySmooth(self.pumpkin_name + "_stem", dv=1)

        cmds.polySphere(name=self.pumpkin_name + '_bottom_stem', r=0.1, sh=10)
        cmds.move(0, -0.51, 0, os=True, wd=True, r=True)
        cmds.scale(1, 0.4, 1)

    def make_pumpkin_circle_cut(self, y, z, scale_x, scale_z, rotation='0deg'):
        cmds.polyCylinder(n="cut", h=1, r=0.05)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4
        z = z-0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(scale_x, 1, scale_z)
        cmds.rotate(0, rotation, '90deg', r=True)

    def make_pumpkin_triangle_cut(self, y, z, scale_x, scale_z, rotation='0deg'):
        cmds.polyPrism(n="cut", w=0.1, l=1)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4
        z = z-0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(scale_x, 1, scale_z)
        cmds.rotate(0, rotation, '90deg', r=True)

    def make_pumpkin_rectangle_cut(self, y, z, scale_y, scale_z, rotation='45deg'):
        cmds.polyCube(n="cut", h=0.1, d=0.1)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4
        z = z-0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(1, scale_y, scale_z)
        cmds.rotate(rotation, 0, 0, r=True)


cmds.file(f=True, new=True)

try:
    cube_dialog.close()
    cube_dialog.deleteLater()
except:
    pass

pumpkin_dialog = PumpkinCreateDialog()
pumpkin_dialog.show()
