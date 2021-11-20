"""
Script generates pumpkins with randomized features
"""

import sys
import random

from PySide2.QtWidgets import QLabel, QSlider, QSpinBox

from PySide2 import QtCore
from PySide2 import QtWidgets
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

        self.mouth_shapes = ['happy', 'sad', 'neutral']
        self.num_pumpkins = 1
        self.add_pointlight = False

    def create_widgets(self):
        self.slider_num_pumpkins = QtWidgets.QSpinBox()
        self.slider_num_pumpkins.setMinimum(1)

        self.create_btn = QtWidgets.QPushButton("Create")

        self.add_pointlight_checkbox = QtWidgets.QCheckBox()

        self.sad_checkbox = QtWidgets.QCheckBox("Sad")
        self.sad_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)

        self.happy_checkbox = QtWidgets.QCheckBox("Happy")
        self.happy_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)

        self.neutral_checkbox = QtWidgets.QCheckBox("Neutral")
        self.neutral_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)

    def create_layouts(self):

        horz_layout = QtWidgets.QHBoxLayout()
        horz_layout.addWidget(QLabel("Number of pumpkins:"))
        horz_layout.addWidget(self.slider_num_pumpkins)

        horz_layout2 = QtWidgets.QHBoxLayout()
        horz_layout2.addWidget(QLabel("Add point light in pumpkin:"))
        horz_layout2.addWidget(self.add_pointlight_checkbox)

        horz_layout3 = QtWidgets.QHBoxLayout()
        horz_layout3.addWidget(QLabel("Mouth:"))
        horz_layout3.addWidget(self.happy_checkbox)
        horz_layout3.addWidget(self.sad_checkbox)
        horz_layout3.addWidget(self.neutral_checkbox)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(horz_layout)
        main_layout.addLayout(horz_layout2)
        main_layout.addLayout(horz_layout3)

        main_layout.addWidget(self.create_btn)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_pumpkins)

        self.slider_num_pumpkins.valueChanged.connect(self.number_changed)

        self.add_pointlight_checkbox.toggled.connect(self.point_light_changed)

        self.sad_checkbox.clicked.connect(lambda: self.emotion_changed("sad"))
        self.neutral_checkbox.clicked.connect(
            lambda: self.emotion_changed("neutral"))
        self.happy_checkbox.clicked.connect(
            lambda: self.emotion_changed("happy"))

    def point_light_changed(self, checked):
        self.add_pointlight = checked

    def emotion_changed(self, shape):
        if shape in self.mouth_shapes:
            self.mouth_shapes.remove(shape)
        else:
            self.mouth_shapes.append(shape)

        #  ensure that at least one mouth shape is selected
        if len(self.mouth_shapes) == 1:
            if self.mouth_shapes[0] == "sad":
                self.sad_checkbox.setDisabled(True)
            elif self.mouth_shapes[0] == "neutral":
                self.neutral_checkbox.setDisabled(True)
            elif self.mouth_shapes[0] == "happy":
                self.happy_checkbox.setDisabled(True)
        else:
            self.sad_checkbox.setEnabled(True)
            self.neutral_checkbox.setEnabled(True)
            self.happy_checkbox.setEnabled(True)

        print(self.mouth_shapes)

    def number_changed(self, value):
        self.num_pumpkins = int(value)

    def create_pumpkins(self):
        """
        Main call to generate multiple pumpkins
        """
        row_width = 3

        offset_between_pumpkins = 2.7
        row = 0
        col = 0
        for pumpkin_number in range(1, self.num_pumpkins + 1):
            # create the pumpkin and move to proper place in the grid
            self.create_single_pumpkin()
            cmds.move(0, row*offset_between_pumpkins,
                      col*offset_between_pumpkins)
            col = col + 1

            if pumpkin_number % row_width == 0 and pumpkin_number != 0:
                row = row + 1
                col = 0

        cmds.select(clear=True)

    def create_single_pumpkin(self):
        # create basic pumpkin geom
        self.create_main_pumpkin()
        self.create_stems()
        cmds.group(em=True, name='pumpkin_cuts')

        # define the cut outs that will make the face
        self.create_eyes()
        self.create_nose()
        self.create_mouth()

        # delete history & remesh
        cmds.select(self.pumpkin_name)
        cmds.delete(ch=True)
        cmds.polyRemesh(maxEdgeLength=0.25,
                        collapseThreshold=0.6, smoothStrength=100)
        cmds.rename('pumpkin_before')

        # boolean operation creates the face
        cmds.polyCBoolOp('pumpkin_before', 'pumpkin_cuts',
                         op=2, cls=2, n=self.pumpkin_name)

        cmds.select(self.pumpkin_name)
        cmds.delete(ch=True)

        cmds.polyUnite(self.pumpkin_name, self.pumpkin_name +
                       "_stem", self.pumpkin_name+"_bottom_stem", ch=False, muv=1)

        cmds.rename(self.pumpkin_name)

        # random scale to have multiple size of pumpkins
        overall_scale = random.uniform(0.7, 1.4)
        cmds.scale(overall_scale + random.uniform(-0.1, 0.15), overall_scale +
                   random.uniform(-0.1, 0.15), overall_scale + random.uniform(-0.1, 0.15))

        bbox = cmds.exactWorldBoundingBox(self.pumpkin_name)
        bottom = [(bbox[0] + bbox[3])/2, bbox[1], (bbox[2] + bbox[5])/2]
        cmds.xform(self.pumpkin_name, piv=bottom, ws=True)

        cmds.move(0, 0, 0, rpr=True)
        # cmds.freeze()
        # cmds.makeIdentity()
        cmds.delete(self.pumpkin_name, constructionHistory=True)
        cmds.makeIdentity(self.pumpkin_name, apply=True, t=1, r=1, s=1, n=0)

        if self.add_pointlight:
            cmds.pointLight(rgb=[1.00, 0.51, 0.18], i=5,
                            n=self.pumpkin_name+"_point_light")

            bbx = cmds.xform(self.pumpkin_name, q=True,
                             bb=True, ws=True)  # world space
            centerX = (bbx[0] + bbx[3]) / 2.0
            centerY = (bbx[1] + bbx[4]) / 2.0
            centerZ = (bbx[2] + bbx[5]) / 2.0

            cmds.move(centerX, centerY, centerZ)

            cmds.group(self.pumpkin_name, self.pumpkin_name +
                       "_point_light", n=self.pumpkin_name)

    def create_main_pumpkin(self):
        # main pumpkin shape is a sphere with some scaling
        cmds.polySphere(n="pumpkin", sh=11, sa=11)
        self.pumpkin_name = cmds.ls(sl=True)[0]
        cmds.scale(1, 0.8, 1)
        cmds.polyMoveVertex(self.pumpkin_name + '.vtx[110]',
                            self.pumpkin_name + '.vtx[0:21]', s=(1, 0.93, 1))

        cmds.polyMoveVertex(self.pumpkin_name + '.vtx[88:109]',
                            self.pumpkin_name + '.vtx[111]', s=(1, 0.93, 1))

        cmds.select(clear=True)

        # create indents on top and bottom of the pumpkin
        cmds.softSelect(sse=1, ssd=0.53, sud=0.5)
        cmds.select(self.pumpkin_name + ".vtx[111]")
        cmds.move(0, -0.5, 0, os=True, wd=True, r=True)

        cmds.select(self.pumpkin_name + ".vtx[110]")
        cmds.move(0, 0.3, 0, os=True, wd=True, r=True)

        cmds.softSelect(sse=0)

        cmds.select(self.pumpkin_name)

        # create the ridges on the pumpkin
        for i in range(220, 231):
            cmds.polySelect(el=i)
            edgeLoop = cmds.ls(sl=True)
            cmds.polyDuplicateEdge(edgeLoop, of=0.1)

        for i in range(220, 231):
            cmds.polySelect(el=i, add=True)

        cmds.scale(0.9, 0.9, 0.9)

        cmds.polySmooth(self.pumpkin_name, dv=1, c=1)

        cmds.select(self.pumpkin_name)
        # gives the pumpkin thickness
        cmds.polyExtrudeFacet(ltz=0.04)
        cmds.select(self.pumpkin_name)

    def create_eyes(self):
        self.left_eye_y = random.uniform(0.75, 0.81)
        self.left_eye_z = random.uniform(0, 0.25)
        self.right_eye_y = random.uniform(0.75, 0.81)
        self.right_eye_z = random.uniform(0.75, 1)
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

        left_eyebrow_y = self.left_eye_y + random.uniform(0.20, 0.21)
        left_eyebrow_z = self.left_eye_z + random.uniform(-0.05, 0.1)
        right_eyebrow_y = self.right_eye_y + random.uniform(0.20, 0.21)
        right_eyebrow_z = self.right_eye_z + random.uniform(-0.05, 0.1)

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
        nose_rotation = str(random.uniform(0, 180))
        random_scale = random.uniform(1.9, 2.2)

        if shape == ['circle']:
            self.make_pumpkin_circle_cut(
                near_center_y, near_center_z, random_scale + 0.5, random_scale, nose_rotation + 'deg')
        elif shape == ['diamond']:
            self.make_pumpkin_rectangle_cut(
                near_center_y, near_center_z, random_scale, random_scale + 0.5, nose_rotation + 'deg')
        else:
            self.make_pumpkin_triangle_cut(
                near_center_y, near_center_z, random_scale, random_scale + 0.5, nose_rotation + 'deg')

    def create_mouth(self):
        mouth_shape = random.sample(self.mouth_shapes, 1)[0]
        cut_type = random.sample(
            [self.make_pumpkin_circle_cut, self.make_pumpkin_rectangle_cut, self.make_pumpkin_triangle_cut], 1)
        self.mouth_cut(cut_type[0], mouth_shape)

    def mouth_cut(self, cut_type, shape):
        mouth_baseline = random.uniform(0, 0.1)
        mouth_top = random.uniform(mouth_baseline+0.1, 0.3)
        number_cuts = random.randrange(5, 8, 2)
        near_center_z = (self.left_eye_z + self.right_eye_z)/2

        level_count = 0
        total_levels = (number_cuts - 1)/2
        number_cuts = number_cuts + 1

        # determine if mouth cuts are close enough to be seperate or if they will make one larger cut
        seperated_mouth_cuts = bool(random.getrandbits(1))

        if(seperated_mouth_cuts):
            base_scale = random.uniform(1, 1.3)
            cut_distance = 0.07
        else:
            base_scale = random.uniform(0.5, 0.8)
            cut_distance = 0.08

        cut_type(mouth_baseline, near_center_z +
                 0.035, 1.5*base_scale, 1.5*base_scale)

        mouth_style = random.sample(['smaller', 'larger'], 1)
        mouth_cut_rotation = str(random.uniform(0, 20))

        for i in range(number_cuts):
            if i % 2 == 0:
                j = (i+1) * -1
                level_count = level_count + 1
            else:
                j = (i + 1)

            cut_z = near_center_z + j * cut_distance

            if shape == 'sad':
                # decrease height at each level for sad face
                cut_y = mouth_top - \
                    float(level_count)/total_levels * \
                    (mouth_top-mouth_baseline)
            elif shape == 'happy':
                # increase height at each level for happy face
                cut_y = mouth_baseline + \
                    float(level_count)/total_levels * \
                    (mouth_top-mouth_baseline)
            else:
                cut_y = mouth_baseline

            # mouth style either has shape of the cuts get larger or smaller towards the ends of the mouth
            if(mouth_style[0] == 'larger'):
                cut_type(cut_y, cut_z, base_scale + (float(level_count)/total_levels),
                         base_scale + (float(level_count)/total_levels), mouth_cut_rotation + 'deg')
            else:
                cut_type(cut_y, cut_z, 2*base_scale + (float(total_levels - level_count)/total_levels),
                         2*base_scale + (float(total_levels - level_count)/total_levels), mouth_cut_rotation + 'deg')

    def create_stems(self):
        # stem is scaled cylinder
        cmds.polyCylinder(name=self.pumpkin_name + "_stem", height=2,
                          subdivisionsAxis=10, subdivisionsHeight=2)
        cmds.scale(0.12, 0.12, 0.12)
        cmds.move(0, 0.67, 0)

        cmds.polySelect(el=10)
        cmds.move(0, -0.07, 0, os=True, wd=True, r=True)

        cmds.select(self.pumpkin_name + "_stem" + ".e[0:9]")
        cmds.scale(random.uniform(2, 2.2), 2, random.uniform(2, 2.2))

        cmds.select(self.pumpkin_name + "_stem" + ".f[21]")

        random_angle = random.uniform(-45, 45)
        cmds.rotate(str(random_angle) + 'deg', 0, 0, r=True)

        # extrude to add to stem length a random amount
        cmds.polyExtrudeFacet(self.pumpkin_name +
                              "_stem" + ".f[21]", t=[random.uniform(0.01, 0.03), random.uniform(0.1, 0.2), random.uniform(0.01, 0.03)])

        # crease and smooth to get final stem
        cmds.select(self.pumpkin_name + "_stem" + ".e[0:9]")
        cmds.polyCrease(value=10)

        cmds.select(self.pumpkin_name + "_stem" + ".e[20:29]")
        cmds.polyCrease(value=5)

        cmds.polySmooth(self.pumpkin_name + "_stem", dv=1)

        cmds.polySphere(name=self.pumpkin_name + '_bottom_stem', r=0.1, sh=10)
        cmds.move(0, -0.51, 0, os=True, wd=True, r=True)
        cmds.scale(1, 0.4, 1)

    def make_pumpkin_circle_cut(self, y, z, scale_x, scale_z, rotation='0deg'):
        """
        Create geometry that will make a circle cut on the pumpkin after boolean is applied
        (y,z) is between (0,0) [bottom left] and (1,1) [top right] of pumpkin face 
        """
        cmds.polyCylinder(n="cut", h=1.5, r=0.05, sa=5, sc=5, sh=5)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4  # map y from 0 to 1 to -0.4 and 0.4
        z = z-0.5  # map z from 0 to 1 to -0.5 and 0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(scale_x, 1, scale_z)
        cmds.rotate(0, rotation, '90deg', r=True)
        cmds.delete(ch=True)

    def make_pumpkin_triangle_cut(self, y, z, scale_x, scale_z, rotation='0deg'):
        """
        Create geometry that will make a triangle cut on the pumpkin after boolean is applied
        (y,z) is between (0,0) [bottom left] and (1,1) [top right] of pumpkin face 
        """
        cmds.polyPrism(n="cut", w=0.1, l=1, sc=5, sh=5)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4  # map y from 0 to 1 to -0.4 and 0.4
        z = z-0.5  # map z from 0 to 1 to -0.5 and 0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(scale_x, 1, scale_z)
        cmds.rotate(0, rotation, '90deg', r=True)
        cmds.delete(ch=True)

    def make_pumpkin_rectangle_cut(self, y, z, scale_y, scale_z, rotation='45deg'):
        """
        Create geometry that will make a rectangle cut on the pumpkin after boolean is applied
        (y,z) is between (0,0) [bottom left] and (1,1) [top right] of pumpkin face 
        """
        cmds.polyCube(n="cut", h=0.1, d=0.1, w=1.3, sh=3, sw=3, sd=3)
        cut_name = cmds.ls(sl=True)[0]
        cmds.parent(cut_name, 'pumpkin_cuts')

        y = 0.8*y-0.4  # map y from 0 to 1 to -0.4 and 0.4
        z = z-0.5  # map z from 0 to 1 to -0.5 and 0.5

        cmds.move(1, y, z, os=True, wd=True, r=True)
        cmds.scale(1, scale_y, scale_z)
        cmds.rotate(rotation, 0, 0, r=True)
        cmds.delete(ch=True)


try:
    pumpkin_dialog.close()
    pumpkin_dialog.deleteLater()
except:
    pass

pumpkin_dialog = PumpkinCreateDialog()
pumpkin_dialog.show()
