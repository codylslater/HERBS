import os
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.functions as fn
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QObject

from .image_stacks import SliceStack
from .slice_stacks import SliceStacks
from .label_tree import LabelTree
from .uuuuuu import *


atlas_rotation_gb_style = '''
QGroupBox {
    background-color: transparent; 
    border: 1px solid gray; 
    border-radius: 3px; 
    padding: 5px;  
    margin-top: 20px
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding-left: 10px;
    padding-right: 3px;
    padding-top: 10px;
}

'''

atlas_tab_spinbox_textedit_style = '''
QLineEdit { 
    background-color: #292929;
    border: 0px;
    color: white;
}

'''

slice_label_btn_style = '''
QPushButton {
    border : None; 
    background: transparent;
    margin: 0px;
    padding-top: 0px;
    border-radius: 0px;
    min-width: 15px;
    min-height: 15px;
}
'''

page_control_style = '''
QLabel{
    border: None;
    color: white;
}

QPushButton{
    border: 1px solid #242424;
    background: #656565;
    border-radius: 4px;
    min-height: 16px;
    width: 30px;
    padding: 5px;
}

QSlider {
    min-height: 20px;
    max-height: 20px;
    background: transparent;
    border: None;
}

QSlider::groove:horizontal {
    border: None;
    height: 2px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 2px 0px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 10px;
    height: 30px;
    margin: -4px -2px; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 0px;
}
'''

sidebar_button_style = '''
QPushButton{
    background: #656565;
    border-radius: 5px;
    color: white;
    border-style: outset;
    border-bottom: 1px solid rgb(30, 30, 30);
    height: 24px;
    margin: 0px;
}

QPushButton:hover{
    background-color: #323232;
    border: 1px solid #656565;
}

QPushButton:checked{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #17bb00, stop: 1 #0e6900);
    border-bottom: 1px solid rgb(30, 30, 30);
    border-top: None;
    border-left: None;
    border-right: None;  
}
'''


class PageController(QWidget):
    class SignalProxy(QObject):
        sigPageChanged = pyqtSignal(object)

    def __init__(self):
        self._sigprox = PageController.SignalProxy()
        self.sig_page_changed = self._sigprox.sigPageChanged

        QWidget.__init__(self)

        self.setStyleSheet(page_control_style)

        self.max_val = None

        self.page_slider = QSlider(Qt.Horizontal)
        self.page_slider.setMinimum(0)
        self.page_slider.valueChanged.connect(self.slider_value_changed)

        self.page_label = QLabel()
        self.page_label.setFixedSize(50, 20)

        self.page_left_btn = QPushButton()
        self.page_left_btn.setIcon(QtGui.QIcon("icons/backward.svg"))
        self.page_left_btn.setIconSize(QtCore.QSize(16, 16))
        self.page_left_btn.clicked.connect(self.left_btn_clicked)

        self.page_right_btn = QPushButton()
        self.page_right_btn.setIcon(QtGui.QIcon("icons/forward.svg"))
        self.page_right_btn.setIconSize(QtCore.QSize(16, 16))
        self.page_right_btn.clicked.connect(self.right_btn_clicked)

        self.page_fast_left_btn = QPushButton()
        self.page_fast_left_btn.setIcon(QtGui.QIcon("icons/fast_backward.svg"))
        self.page_fast_left_btn.setIconSize(QtCore.QSize(16, 16))
        self.page_fast_left_btn.clicked.connect(self.fast_left_btn_clicked)

        self.page_fast_right_btn = QPushButton()
        self.page_fast_right_btn.setIcon(QtGui.QIcon("icons/fast_forward.svg"))
        self.page_fast_right_btn.setIconSize(QtCore.QSize(16, 16))
        self.page_fast_right_btn.clicked.connect(self.fast_right_btn_clicked)

        page_ctrl_layout = QHBoxLayout()
        page_ctrl_layout.setSpacing(0)
        page_ctrl_layout.setContentsMargins(10, 5, 10, 5)
        page_ctrl_layout.addWidget(self.page_left_btn)
        page_ctrl_layout.addSpacing(10)
        page_ctrl_layout.addWidget(self.page_fast_left_btn)
        page_ctrl_layout.addSpacing(10)
        page_ctrl_layout.addWidget(self.page_slider)
        page_ctrl_layout.addSpacing(5)
        page_ctrl_layout.addWidget(self.page_label)
        page_ctrl_layout.addWidget(self.page_fast_right_btn)
        page_ctrl_layout.addSpacing(10)
        page_ctrl_layout.addWidget(self.page_right_btn)

        self.setLayout(page_ctrl_layout)

    def set_val(self, val):
        self.page_slider.setValue(val)

    def set_max(self, val):
        self.max_val = val
        self.page_slider.setMaximum(val)

    def slider_value_changed(self):
        val = self.page_slider.value()
        self.page_label.setText(str(val))
        self.sig_page_changed.emit(val)

    def left_btn_clicked(self):
        val = self.page_slider.value() - 1
        if val < 0:
            val = 0
        self.set_val(val)

    def right_btn_clicked(self):
        val = self.page_slider.value() + 1
        if val > self.max_val:
            val = self.max_val
        self.set_val(val)

    def fast_left_btn_clicked(self):
        val = self.page_slider.value() - 10
        if val < 0:
            val = 0
        self.set_val(val)

    def fast_right_btn_clicked(self):
        val = self.page_slider.value() + 10
        if val > self.max_val:
            val = self.max_val
        self.set_val(val)


class SliceRotation(QWidget):

    class SignalProxy(QObject):
        sigSliceRotated = pyqtSignal(object)  # id

    def __init__(self):
        self._sigprox = SliceRotation.SignalProxy()
        self.sig_slice_rotated = self._sigprox.sigSliceRotated

        QWidget.__init__(self)

        self.prec = 0.01
        self.rot_range = 30
        self.n_steps = int(self.rot_range / self.prec)

        self.h_slider = QSlider(Qt.Horizontal)
        self.h_slider.sliderMoved.connect(self.h_slider_changed)
        self.h_slider.setValue(0)
        self.h_slider.setRange(-self.n_steps, self.n_steps)

        self.h_spinbox = QDoubleSpinBox()
        self.h_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
        self.h_spinbox.valueChanged.connect(self.h_spinbox_changed)
        self.h_spinbox.setDecimals(2)
        self.h_spinbox.setValue(0)
        self.h_spinbox.setRange(-self.rot_range, self.rot_range)
        self.h_spinbox.setSingleStep(self.prec)
        self.h_spinbox.setMinimumSize(50, 20)

        self.v_slider = QSlider(Qt.Horizontal)
        self.v_slider.sliderMoved.connect(self.v_slider_changed)
        self.v_slider.setValue(0)
        self.v_slider.setRange(-self.n_steps, self.n_steps)

        self.v_spinbox = QDoubleSpinBox()
        self.v_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
        self.v_spinbox.valueChanged.connect(self.v_spinbox_changed)
        self.v_spinbox.setDecimals(2)
        self.v_spinbox.setValue(0)
        self.v_spinbox.setRange(-self.rot_range, self.rot_range)
        self.v_spinbox.setSingleStep(self.prec)
        self.v_spinbox.setMinimumSize(50, 20)

    def set_prec(self, prec):
        self.prec = prec

    def h_slider_changed(self):
        val = self.h_slider.value() * self.prec
        self.h_spinbox.setValue(val)

    def h_spinbox_changed(self):
        val = int(self.h_spinbox.value() / self.prec)
        self.h_slider.setValue(val)
        self.sig_slice_rotated.emit(np.deg2rad([self.h_spinbox.value(), self.v_spinbox.value()]))

    def v_slider_changed(self):
        val = self.v_slider.value() * self.prec
        self.v_spinbox.setValue(val)

    def v_spinbox_changed(self):
        val = int(self.v_spinbox.value() / self.prec)
        self.v_slider.setValue(val)
        self.sig_slice_rotated.emit(np.deg2rad([self.h_spinbox.value(), self.v_spinbox.value()]))


class ImageLabel(QWidget):
    def __init__(self, img, title):
        super(QWidget, self).__init__()
        layout = QHBoxLayout(self)
        self.label3 = QLabel(self)
        self.title = QLabel(title)
        self.pixmap = QPixmap(img)
        self.pixmap = self.pixmap.scaled(QSize(20, 10))
        self.label3.setPixmap(self.pixmap)
        self.label3.setAlignment(Qt.AlignCenter)
        self.title.setMinimumHeight(self.pixmap.height())
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label3)
        layout.addWidget(self.title)
        self.label3.setStyleSheet('background-color: transparent;')
        self.title.setStyleSheet("""
            background-color: transparent;
            color: black;
            padding: 0px 3px 0px 0px;
        """)
        layout.setSpacing(0)
        layout.addStretch()


class RotationBtn(QPushButton):
    def __init__(self, icon_path):
        super(QPushButton, self).__init__()
        self.setStyleSheet(slice_label_btn_style)
        self.setFixedSize(15, 15)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(15, 15))


class AtlasView(QObject):
    """
    A collection of user interface elements bound together:


    """
    def __init__(self):
        super(AtlasView, self).__init__()
        QObject.__init__(self)

        self.atlas_data = None
        self.atlas_label = None
        self.atlas_info = None
        self.label_info = None
        self.atlas_contour = None
        self.atlas_boundary = None
        self.coronal_size = None
        self.sagital_size = None
        self.horizontal_size = None
        self.slice_size = None
        self.slice_tb_size_base = 80
        self.coronal_tb_size = None
        self.sagital_tb_size = None
        self.horizontal_tb_size = None
        self.slice_tb_size = None

        self.slice_image_data = None
        self.processing_slice = None
        self.slice_cut = 'Coronal'
        self.slice_width = 0
        self.slice_height = 0
        self.slice_distance = 0
        self.slice_bregma = []
        self.slice_boundary_points = []
        self.slice_info_ready = False

        self.label_level = None

        self.coronal_rotated = False
        self.sagital_rotated = False
        self.horizontal_rotated = False

        self.atlas_size = None
        self.anterior_info = None
        self.dorsal_info = None
        self.right_info = None
        self.vox_size_um = None
        self.Bregma = None
        self.rotate_origin_3d = None
        self.origin_3d = None

        self.c_size = None
        self.s_size = None
        self.h_size = None

        self.c_rotm_2d = None
        self.s_rotm_2d = None
        self.h_rotm_2d = None

        self.c_rotm_3d = None
        self.s_rotm_3d = None
        self.h_rotm_3d = None

        self.side_lines = None
        self.corner_points = None

        self.current_coronal_index = None
        self.current_sagital_index = None
        self.current_horizontal_index = None

        self.anchor_coronal_index = None
        self.anchor_sagital_index = None
        self.anchor_horicontal_index = None


        self.display_atlas = None
        self.display_label = None
        self.scale = None
        self.interpolate = True
        self.oy_vector = np.array([0, 1, 0])
        self.oz_vector = np.array([0, 0, 1])
        self.ox_vector = np.array([1, 0, 0])

        self.axis = gl.GLAxisItem()
        self.axis.setSize(250, 700, 250)

        self.grid = gl.GLGridItem()
        self.grid.scale(2, 2, 1)

        self.mesh = gl.GLMeshItem(smooth=True, color=[0.5, 0.5, 0.5, 0.2], shader='balloon')
        self.mesh.setGLOptions('additive')

        # 3d things
        plate_color = [0.5, 0.5, 0.5, 0.2]
        self.ap_plate_verts = np.array([[-1, 0, -1], [-1, 0, 1], [1, 0, 1], [1, 0, -1]])
        self.ap_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        ap_plate_md = gl.MeshData(vertexes=self.ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh = gl.GLMeshItem(meshdata=ap_plate_md, smooth=False, color=plate_color)
        self.ap_plate_mesh.setGLOptions('additive')

        self.dv_plate_verts = np.array([[-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0]])
        self.dv_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        dv_plate_md = gl.MeshData(vertexes=self.dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh = gl.GLMeshItem(meshdata=dv_plate_md, smooth=False, color=plate_color)
        self.dv_plate_mesh.setGLOptions('additive')

        self.ml_plate_verts = np.array([[0, -1, -1], [0, 1, -1], [0, 1, 1], [0, -1, 1]])
        self.ml_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])
        ml_plate_md = gl.MeshData(vertexes=self.ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh = gl.GLMeshItem(meshdata=ml_plate_md, smooth=False, color=plate_color)
        self.ml_plate_mesh.setGLOptions('additive')

        # ap - coronal
        self.cimg = SliceStacks()
        self.cpage_ctrl = PageController()
        self.cpage_ctrl.sig_page_changed.connect(self.coronal_slice_page_changed)
        self.clut = pg.HistogramLUTWidget()
        self.clut.setImageItem(self.cimg.img)

        self.simg = SliceStacks()
        self.spage_ctrl = PageController()
        self.spage_ctrl.sig_page_changed.connect(self.sagital_slice_page_changed)
        self.slut = pg.HistogramLUTWidget()
        self.slut.setImageItem(self.simg.img)

        self.himg = SliceStacks()
        self.hpage_ctrl = PageController()
        self.hpage_ctrl.sig_page_changed.connect(self.horizontal_slice_page_changed)
        self.hlut = pg.HistogramLUTWidget()
        self.hlut.setImageItem(self.himg.img)

        self.label_tree = LabelTree()

        self.working_atlas = self.cimg
        self.working_page_control = self.cpage_ctrl

        self.slice_stack = SliceStack()


        # radio buttons
        self.radio_group = QFrame()
        self.radio_group.setFixedHeight(50)
        self.radio_group.setStyleSheet('QFrame{border: 1px solid gray; border-radius: 3px}')
        radio_group_layout = QHBoxLayout(self.radio_group)
        radio_group_layout.setContentsMargins(5, 0, 5, 0)
        radio_group_layout.setAlignment(Qt.AlignCenter)
        self.section_rabnt1 = QRadioButton('Coronal')
        self.section_rabnt1.setChecked(True)
        self.section_rabnt2 = QRadioButton('Sagittal')
        self.section_rabnt3 = QRadioButton('Horizontal')
        self.section_rabnt1.setStyleSheet('color: white')
        self.section_rabnt2.setStyleSheet('color: white')
        self.section_rabnt3.setStyleSheet('color: white')
        radio_group_layout.addWidget(self.section_rabnt1)
        radio_group_layout.addWidget(self.section_rabnt2)
        radio_group_layout.addWidget(self.section_rabnt3)

        # angles
        self.crotation_ctrl = SliceRotation()
        self.crotation_ctrl.sig_slice_rotated.connect(self.coronal_slice_rotated)
        self.srotation_ctrl = SliceRotation()
        self.srotation_ctrl.sig_slice_rotated.connect(self.sagital_slice_rotated)
        self.hrotation_ctrl = SliceRotation()
        self.hrotation_ctrl.sig_slice_rotated.connect(self.horizontal_slice_rotated)


        # opacity
        atlas_op_label = QLabel('Opacity: ')
        self.atlas_op_slider = QSlider(QtCore.Qt.Horizontal)
        self.atlas_op_slider.setValue(100)
        self.atlas_op_slider.setMinimum(0)
        self.atlas_op_slider.setMaximum(100)
        self.atlas_op_slider.sliderMoved.connect(self.change_opacity_spinbox_value)
        # self.atlas_op_slider.valueChanged.connect(self.sig_rescale_slider)

        self.atlas_op_spinbox = QDoubleSpinBox()
        self.atlas_op_spinbox.lineEdit().setStyleSheet(atlas_tab_spinbox_textedit_style)
        self.atlas_op_spinbox.setValue(1)
        self.atlas_op_spinbox.setRange(0, 1)
        self.atlas_op_spinbox.setSingleStep(0.05)
        self.atlas_op_spinbox.setMinimumSize(50, 20)
        self.atlas_op_spinbox.valueChanged.connect(self.opacity_changed)

        opacity_wrap = QFrame()
        opacity_layout = QHBoxLayout(opacity_wrap)
        opacity_layout.setSpacing(2)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.addWidget(atlas_op_label)
        opacity_layout.addWidget(self.atlas_op_slider)
        opacity_layout.addWidget(self.atlas_op_spinbox)

        # boundary
        self.show_boundary_btn = QPushButton('Show Boundary')
        self.show_boundary_btn.setStyleSheet(sidebar_button_style)
        self.show_boundary_btn.setCheckable(True)

        #
        self.navigation_btn = QPushButton('Navigation')
        self.navigation_btn.setStyleSheet(sidebar_button_style)
        self.navigation_btn.setCheckable(True)
        self.navigation_btn.clicked.connect(self.navigation_btn_clicked)

        # coronal section control
        coronal_rotation_wrap = QGroupBox('Coronal Section')
        coronal_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        coronal_wrap_layout = QGridLayout(coronal_rotation_wrap)
        coronal_wrap_layout.setContentsMargins(0, 0, 0, 0)
        coronal_wrap_layout.setSpacing(10)

        c_section_label_img = QPixmap('icons/sidebar/c_section.png')
        c_section_label_img = c_section_label_img.scaled(QSize(40, 40))
        c_section_label = QLabel('Tilt Z: ')
        c_section_label.setPixmap(c_section_label_img)

        c_lr_btn = RotationBtn("icons/sidebar/rotation_horizontal.svg")
        c_ud_btn = RotationBtn("icons/sidebar/rotation_vertical.svg")

        coronal_wrap_layout.addWidget(c_section_label, 0, 0, 2, 1)
        coronal_wrap_layout.addWidget(c_lr_btn, 0, 1, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.h_slider, 0, 2, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.h_spinbox, 0, 3, 1, 1)
        coronal_wrap_layout.addWidget(c_ud_btn, 1, 1, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.v_slider, 1, 2, 1, 1)
        coronal_wrap_layout.addWidget(self.crotation_ctrl.v_spinbox, 1, 3, 1, 1)

        # sagital section control
        sagital_rotation_wrap = QGroupBox('Sagittal Section')
        sagital_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        sagital_wrap_layout = QGridLayout(sagital_rotation_wrap)
        sagital_wrap_layout.setContentsMargins(0, 0, 0, 0)
        sagital_wrap_layout.setSpacing(10)

        s_section_label_img = QPixmap('icons/sidebar/s_section.png')
        s_section_label_img = s_section_label_img.scaled(QSize(40, 40))
        s_section_label = QLabel()
        s_section_label.setPixmap(s_section_label_img)

        s_lr_btn = RotationBtn("icons/sidebar/rotation_horizontal.svg")
        s_ud_btn = RotationBtn("icons/sidebar/rotation_vertical.svg")

        sagital_wrap_layout.addWidget(s_section_label, 0, 0, 2, 1)
        sagital_wrap_layout.addWidget(s_lr_btn, 0, 1, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.h_slider, 0, 2, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.h_spinbox, 0, 3, 1, 1)
        sagital_wrap_layout.addWidget(s_ud_btn, 1, 1, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.v_slider, 1, 2, 1, 1)
        sagital_wrap_layout.addWidget(self.srotation_ctrl.v_spinbox, 1, 3, 1, 1)

        # horizontal section control
        horizontal_rotation_wrap = QGroupBox('Horizontal Section')
        horizontal_rotation_wrap.setStyleSheet(atlas_rotation_gb_style)
        horizontal_wrap_layout = QGridLayout(horizontal_rotation_wrap)
        horizontal_wrap_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_wrap_layout.setSpacing(10)

        h_section_label_img = QPixmap('icons/sidebar/h_section.png')
        h_section_label_img = h_section_label_img.scaled(QSize(40, 40))
        h_section_label = QLabel()
        h_section_label.setPixmap(h_section_label_img)

        h_lr_btn = RotationBtn("icons/sidebar/rotation_horizontal.svg")
        h_ud_btn = RotationBtn("icons/sidebar/rotation_vertical.svg")

        horizontal_wrap_layout.addWidget(h_section_label, 0, 0, 2, 1)
        horizontal_wrap_layout.addWidget(h_lr_btn, 0, 1, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.h_slider, 0, 2, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.h_spinbox, 0, 3, 1, 1)
        horizontal_wrap_layout.addWidget(h_ud_btn, 1, 1, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.v_slider, 1, 2, 1, 1)
        horizontal_wrap_layout.addWidget(self.hrotation_ctrl.v_spinbox, 1, 3, 1, 1)

        self.sidebar_wrap = QFrame()
        sidebar_wrap_layout = QVBoxLayout(self.sidebar_wrap)
        sidebar_wrap_layout.setSpacing(0)
        sidebar_wrap_layout.addWidget(self.radio_group)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(opacity_wrap)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(self.show_boundary_btn)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(coronal_rotation_wrap)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(sagital_rotation_wrap)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(horizontal_rotation_wrap)
        sidebar_wrap_layout.addSpacing(10)
        sidebar_wrap_layout.addWidget(self.navigation_btn)

        # self.lut.sigLookupTableChanged.connect(self.histlut_changed)
        # self.lut.sigLevelsChanged.connect(self.histlut_changed)

    def reset_3d_plates(self):
        self.ap_plate_verts = np.array([[-1, 0, -1], [-1, 0, 1], [1, 0, 1], [1, 0, -1]])
        self.ap_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])

        self.dv_plate_verts = np.array([[-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0]])
        self.dv_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])

        self.ml_plate_verts = np.array([[0, -1, -1], [0, 1, -1], [0, 1, 1], [0, -1, 1]])
        self.ml_plate_faces = np.array([[0, 1, 2], [0, 2, 3]])

    def set_slice_data(self, slice_data):
        self.slice_image_data = slice_data.copy()
        self.slice_stack.set_data(slice_data)
        self.slice_size = np.ravel(self.slice_stack.img_layer.image.shape[:2])
        slice_scale = np.max(self.slice_size / self.slice_tb_size_base)
        self.slice_tb_size = self.slice_size / slice_scale
        self.slice_tb_size = self.slice_tb_size[::-1].astype(int)

        self.working_atlas = self.slice_stack

        rect = (0, 0, int(self.slice_size[1]), int(self.slice_size[0]))
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.working_atlas.image_dict['tri_pnts'].set_range(x_range=self.slice_size[1] - 1,
                                                            y_range=self.slice_size[0] - 1)

    def set_slice_info(self, slice_info):
        self.slice_cut = slice_info.cut
        self.slice_width = slice_info.width
        self.slice_height = slice_info.height
        self.slice_distance = slice_info.distance
        if self.slice_height == 0 or self.slice_width == 0 or self.slice_distance == 0 or not self.slice_bregma:
            self.slice_info_ready = False
        else:
            self.slice_info_ready = True

    def save_slice_data_and_info(self):
        data = {'data': self.slice_image_data,
                'cut': self.slice_cut,
                'width': self.slice_width,
                'height': self.slice_height,
                'distance': self.slice_distance,
                'Bregma': self.slice_bregma,
                'ready': self.slice_info_ready}
        return data

    def set_slice_data_and_info(self, slice_data):
        img_data = slice_data['data'].copy()
        self.slice_cut = slice_data['cut']
        self.slice_width = slice_data['width']
        self.slice_height = slice_data['height']
        self.slice_distance = slice_data['distance']
        self.slice_bregma = slice_data['Bregma']
        self.slice_info_ready = slice_data['ready']
        self.set_slice_data(img_data)

    def get_slice_coords(self, ruler_data):
        x, y, z = get_slice_atlas_coord(ruler_data, self.slice_cut, self.slice_size,
                                        self.slice_width, self.slice_height, self.slice_distance, self.slice_bregma)
        return x, y, z

    def check_info_ready(self):
        if self.slice_height == 0 or self.slice_width == 0 or self.slice_distance == 0:
            self.slice_info_ready = False
        else:
            self.slice_info_ready = True



    def clear_slice_info(self):
        if self.slice_image_data is not None:
            self.slice_cut = 'Coronal'
            self.slice_width = 0
            self.slice_height = 0
            self.slice_distance = 0
            self.slice_bregma = []
            self.slice_info_ready = False
        else:
            return

    def set_data(self, atlas_data, atlas_label, atlas_info, label_info, boundaries):
        if self.atlas_data is not None:
            print('sdfsdfd')
            self.reset_3d_plates()

        self.atlas_data = atlas_data
        self.atlas_label = atlas_label
        self.label_info = label_info
        self.atlas_boundary = boundaries
        self.label_tree.set_labels(label_info)

        self.atlas_size = self.atlas_data.shape
        self.anterior_info = atlas_info[0]
        self.dorsal_info = atlas_info[1]
        self.right_info = atlas_info[2]
        self.vox_size_um = atlas_info[3]['vxsize']

        if np.all(np.ravel(atlas_info[3]['Bregma']) == 0):
            da_bregma = (int(self.atlas_size[1] / 2), int(self.atlas_size[2] / 2), int(self.atlas_size[0] / 2))
        else:
            da_bregma = atlas_info[3]['Bregma']
        inverse_b2 = self.atlas_size[0] - 1 - da_bregma[2]
        self.Bregma = (inverse_b2, da_bregma[0], da_bregma[1])
        print(self.Bregma, 'bregma')
        self.rotate_origin_3d = np.array(da_bregma)
        self.origin_3d = np.array(da_bregma)

        self.current_coronal_index = self.origin_3d[1]
        self.current_sagital_index = self.origin_3d[0]
        self.current_horizontal_index = self.origin_3d[2]

        self.cpage_ctrl.set_max(self.atlas_size[2] - 1)
        self.spage_ctrl.set_max(self.atlas_size[1] - 1)
        self.hpage_ctrl.set_max(self.atlas_size[0] - 1)

        if self.current_coronal_index == 0:
            self.coronal_slice_page_changed(self.current_coronal_index)
            self.cpage_ctrl.page_label.setText('0')
        else:
            self.cpage_ctrl.set_val(self.current_coronal_index)

        if self.current_sagital_index == 0:
            self.sagital_slice_page_changed(self.current_sagital_index)
            self.spage_ctrl.page_label.setText('0')
        else:
            self.spage_ctrl.set_val(self.current_sagital_index)

        if self.current_horizontal_index == 0:
            self.horizontal_slice_page_changed(self.current_horizontal_index)
            self.hpage_ctrl.page_label.setText('0')
        else:
            self.hpage_ctrl.set_val(self.current_horizontal_index)

        self.cimg.label_img.setLevels(levels=[0, self.label_tree.label_level])
        self.simg.label_img.setLevels(levels=[0, self.label_tree.label_level])
        self.himg.label_img.setLevels(levels=[0, self.label_tree.label_level])

        lut = self.label_tree.lookup_table()
        self.cimg.label_img.setLookupTable(lut=lut)
        self.simg.label_img.setLookupTable(lut=lut)
        self.himg.label_img.setLookupTable(lut=lut)

        self.c_size = np.array([self.atlas_size[0], self.atlas_size[1]])
        coronal_scale = np.max(self.c_size / self.slice_tb_size_base)
        self.coronal_tb_size = self.c_size[::-1] / coronal_scale
        self.coronal_tb_size = self.coronal_tb_size.astype(int)

        self.s_size = np.array([self.atlas_size[0], self.atlas_size[2]])
        sagital_scale = np.max(self.s_size / self.slice_tb_size_base)
        self.sagital_tb_size = self.s_size[::-1] / sagital_scale
        self.sagital_tb_size = self.sagital_tb_size.astype(int)

        self.h_size = np.array([self.atlas_size[1], self.atlas_size[2]])
        horizontal_scale = np.max(self.h_size / self.slice_tb_size_base)
        self.horizontal_tb_size = self.h_size[::-1] / horizontal_scale
        self.horizontal_tb_size = self.horizontal_tb_size.astype(int)

        self.update_3d_plate_component()

    def update_3d_plate_component(self):
        self.ap_plate_verts[:, 0] = self.ap_plate_verts[:, 0] * self.atlas_size[1] * 0.5
        self.ap_plate_verts[:, 2] = self.ap_plate_verts[:, 2] * self.atlas_size[0] * 0.5

        self.dv_plate_verts[:, 0] = self.dv_plate_verts[:, 0] * self.atlas_size[1] * 0.5
        self.dv_plate_verts[:, 1] = self.dv_plate_verts[:, 1] * self.atlas_size[2] * 0.5

        self.ml_plate_verts[:, 1] = self.ml_plate_verts[:, 1] * self.atlas_size[2] * 0.5
        self.ml_plate_verts[:, 2] = self.ml_plate_verts[:, 2] * self.atlas_size[0] * 0.5

        z_slide_dist = (self.atlas_size[0] * 0.5 - self.origin_3d[2])
        y_slide_dist = (self.atlas_size[2] * 0.5 - self.origin_3d[1])
        x_slide_dist = (self.atlas_size[1] * 0.5 - self.origin_3d[0])

        self.ap_plate_verts = self.ap_plate_verts + np.array([x_slide_dist, 0, z_slide_dist])
        self.dv_plate_verts = self.dv_plate_verts + np.array([x_slide_dist, y_slide_dist, 0])
        self.ml_plate_verts = self.ml_plate_verts + np.array([0, y_slide_dist, z_slide_dist])

        ap_plate_md = gl.MeshData(vertexes=self.ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh.setMeshData(meshdata=ap_plate_md)

        dv_plate_md = gl.MeshData(vertexes=self.dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh.setMeshData(meshdata=dv_plate_md)

        ml_plate_md = gl.MeshData(vertexes=self.ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh.setMeshData(meshdata=ml_plate_md)

    def working_cut_changed(self, atlas_display):
        self.pre_trajectory_changed()
        if atlas_display == "coronal":
            self.working_atlas = self.cimg
            self.working_page_control = self.cpage_ctrl
            self.slice_tb_size = self.coronal_tb_size
            self.slice_size = self.c_size
        elif atlas_display == "sagittal":
            self.working_atlas = self.simg
            self.working_page_control = self.spage_ctrl
            self.slice_tb_size = self.sagital_tb_size
            self.slice_size = self.s_size
        else:
            self.working_atlas = self.himg
            self.working_page_control = self.hpage_ctrl
            self.slice_tb_size = self.horizontal_tb_size
            self.slice_size = self.h_size
        rect = (0, 0, int(self.slice_size[1]), int(self.slice_size[0]))
        self.corner_points, self.side_lines = get_corner_line_from_rect(rect)
        self.working_atlas.image_dict['tri_pnts'].set_range(x_range=self.slice_size[1] - 1,
                                                            y_range=self.slice_size[0] - 1)

    def navigation_btn_clicked(self):
        if self.navigation_btn.isChecked():
            self.cimg.v_line.setVisible(True)
            self.cimg.h_line.setVisible(True)
            self.himg.v_line.setVisible(True)
            self.himg.h_line.setVisible(True)
            self.simg.v_line.setVisible(True)
            self.simg.h_line.setVisible(True)
        else:
            self.cimg.v_line.setVisible(False)
            self.cimg.h_line.setVisible(False)
            self.himg.v_line.setVisible(False)
            self.himg.h_line.setVisible(False)
            self.simg.v_line.setVisible(False)
            self.simg.h_line.setVisible(False)

    def change_opacity_spinbox_value(self):
        val = self.atlas_op_slider.value()
        self.atlas_op_spinbox.setValue(val / 100)

    def opacity_changed(self):
        val = self.atlas_op_spinbox.value()
        self.atlas_op_slider.setValue(val * 100)
        self.cimg.label_img.setOpts(opacity=val)
        self.simg.label_img.setOpts(opacity=val)
        self.himg.label_img.setOpts(opacity=val)

    # slice number changed
    def coronal_slice_page_changed(self, page_number):
        self.crotation_ctrl.h_spinbox.setValue(0)
        self.crotation_ctrl.v_spinbox.setValue(0)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_coronal_index = page_number
        da_atlas_slice = self.atlas_data[:, :, page_number]
        da_atlas_label = self.atlas_label[:, :, page_number]
        da_atlas_contour = self.atlas_boundary['c_contour'][:, :, page_number]
        self.cimg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)

        slide_dist = (page_number - self.origin_3d[1])
        ap_plate_verts = self.ap_plate_verts + np.array([0, slide_dist, 0])
        ap_plate_md = gl.MeshData(vertexes=ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh.setMeshData(meshdata=ap_plate_md)
        self.get_3d_origin()

    def sagital_slice_page_changed(self, page_number):
        self.srotation_ctrl.h_spinbox.setValue(0)
        self.srotation_ctrl.v_spinbox.setValue(0)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_sagital_index = page_number
        da_atlas_slice = self.atlas_data[:, page_number, :]
        da_atlas_label = self.atlas_label[:, page_number, :]
        da_atlas_contour = self.atlas_boundary['s_contour'][:, page_number, :]
        self.simg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)

        slide_dist = (page_number - self.origin_3d[0])
        ml_plate_verts = self.ml_plate_verts + np.array([slide_dist, 0, 0])
        ml_plate_md = gl.MeshData(vertexes=ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh.setMeshData(meshdata=ml_plate_md)
        self.get_3d_origin()

    def horizontal_slice_page_changed(self, page_number):
        self.hrotation_ctrl.h_spinbox.setValue(0)
        self.hrotation_ctrl.v_spinbox.setValue(0)
        if self.atlas_data is None or self.atlas_label is None:
            return
        self.current_horizontal_index = page_number
        slice_number = self.atlas_size[0] - 1 - page_number
        da_atlas_slice = self.atlas_data[slice_number, :, :]
        da_atlas_label = self.atlas_label[slice_number, :, :]
        da_atlas_contour = self.atlas_boundary['h_contour'][slice_number, :, :]
        self.himg.set_data(da_atlas_slice, da_atlas_label, da_atlas_contour, scale=None)

        slide_dist = (page_number - self.origin_3d[2])
        dv_plate_verts = self.dv_plate_verts + np.array([0, 0, slide_dist])
        dv_plate_md = gl.MeshData(vertexes=dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh.setMeshData(meshdata=dv_plate_md)
        self.get_3d_origin()

    def get_3d_origin(self):
        c_id = self.current_coronal_index
        s_id = self.current_sagital_index
        h_id = self.current_horizontal_index
        o_rot = np.array([s_id, c_id, h_id])
        self.rotate_origin_3d = o_rot - self.origin_3d

    def coronal_slice_rotated(self, rads):
        if self.atlas_data is None or self.atlas_label is None:
            return
        if np.all(np.ravel(rads) == 0):
            self.coronal_rotated = False
            return

        self.coronal_rotated = True

        # calculate for 2d rotation
        c_id = self.current_coronal_index
        s_id = self.current_sagital_index
        h_id = self.atlas_size[0] - self.current_horizontal_index

        z_angle = rads[0]
        x_angle = rads[1]
        self.c_rotm_2d = np.dot(rotation_x(z_angle), rotation_y(x_angle))

        o_val = np.array([0, 0, c_id])
        o_rot = np.array([h_id, s_id, c_id])

        oz_vector = np.dot(self.c_rotm_2d, np.array([1, 0, 0]))
        ox_vector = np.dot(self.c_rotm_2d, np.array([0, 1, 0]))

        oval_new = o_rot + np.dot(self.c_rotm_2d, o_val - o_rot)

        ox_length = self.atlas_size[1]
        oz_length = self.atlas_size[0]

        atlas = fn.affineSlice(self.atlas_data, shape=(oz_length, ox_length), vectors=[oz_vector, ox_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(oz_length, ox_length), vectors=[oz_vector, ox_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
        da_contour = make_contour_img(label)
        self.cimg.set_data(atlas, label, da_contour, scale=None)

        self.c_rotm_3d = np.dot(rotation_z(z_angle), rotation_x(-x_angle))

        slide_dist = self.current_coronal_index - self.origin_3d[1]
        ap_plate_verts = self.ap_plate_verts + np.array([0, slide_dist, 0])
        ap_plate_verts = np.dot(self.c_rotm_3d, (ap_plate_verts - self.rotate_origin_3d).T).T + self.rotate_origin_3d
        ap_plate_md = gl.MeshData(vertexes=ap_plate_verts, faces=self.ap_plate_faces)
        self.ap_plate_mesh.setMeshData(meshdata=ap_plate_md)

    def sagital_slice_rotated(self, rads):
        if self.atlas_data is None or self.atlas_label is None:
            return
        if np.all(np.ravel(rads) == 0):
            self.sagital_rotated = False
            return

        self.sagital_rotated = True

        c_id = self.current_coronal_index
        s_id = self.current_sagital_index
        h_id = self.current_horizontal_index

        z_angle = rads[0]
        y_angle = rads[1]
        self.s_rotm_2d = np.dot(rotation_x(z_angle), rotation_z(y_angle))

        o_val = np.array([0, s_id, 0])
        o_rot = np.array([h_id, s_id, c_id])

        oz_vector = np.dot(self.s_rotm_2d, np.array([1, 0, 0]))
        oy_vector = np.dot(self.s_rotm_2d, np.array([0, 0, 1]))

        oval_new = o_rot + np.dot(self.s_rotm_2d, o_val - o_rot)

        oy_length = self.atlas_size[2]
        oz_length = self.atlas_size[0]

        atlas = fn.affineSlice(self.atlas_data, shape=(oz_length, oy_length), vectors=[oz_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(oz_length, oy_length), vectors=[oz_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
        da_contour = make_contour_img(label)
        self.simg.set_data(atlas, label, da_contour, scale=None)

        self.s_rotm_3d = np.dot(rotation_z(z_angle), rotation_y(-y_angle))

        slide_dist = (self.current_sagital_index - self.Bregma[1])
        ml_plate_verts = self.ml_plate_verts + np.array([slide_dist, 0, 0])
        ml_plate_verts = np.dot(self.s_rotm_3d, (ml_plate_verts - self.rotate_origin_3d).T).T + self.rotate_origin_3d
        ml_plate_md = gl.MeshData(vertexes=ml_plate_verts, faces=self.ml_plate_faces)
        self.ml_plate_mesh.setMeshData(meshdata=ml_plate_md)

    def horizontal_slice_rotated(self, rads):
        if self.atlas_data is None or self.atlas_label is None:
            return
        if np.all(np.ravel(rads) == 0):
            self.horizontal_rotated = False
            return

        self.horizontal_rotated = True

        c_id = self.current_coronal_index
        s_id = self.current_sagital_index
        h_id = self.current_horizontal_index

        x_angle = rads[0]
        y_angle = rads[1]
        self.h_rotm_2d = np.dot(rotation_z(y_angle), rotation_y(x_angle))

        o_val = np.array([h_id, 0, 0])
        o_rot = np.array([h_id, s_id, c_id])

        ox_vector = np.dot(self.h_rotm_2d, np.array([0, 1, 0]))
        oy_vector = np.dot(self.h_rotm_2d, np.array([0, 0, 1]))

        oval_new = o_rot + np.dot(self.h_rotm_2d, o_val - o_rot)

        oy_length = self.atlas_size[2]
        ox_length = self.atlas_size[1]

        atlas = fn.affineSlice(self.atlas_data, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=1)
        label = fn.affineSlice(self.atlas_label, shape=(ox_length, oy_length), vectors=[ox_vector, oy_vector],
                               origin=(oval_new[0], oval_new[1], oval_new[2]), axes=(0, 1, 2), order=0)
        da_contour = make_contour_img(label)
        self.himg.set_data(atlas, label, da_contour, scale=None)

        self.h_rotm_3d = np.dot(rotation_y(-y_angle), rotation_x(-x_angle))

        slide_dist = (self.Bregma[0] - h_id)
        dv_plate_verts = self.dv_plate_verts + np.array([0, 0, slide_dist])
        dv_plate_verts = np.dot(self.h_rotm_3d, (dv_plate_verts - self.rotate_origin_3d).T).T + self.rotate_origin_3d
        dv_plate_md = gl.MeshData(vertexes=dv_plate_verts, faces=self.dv_plate_faces)
        self.dv_plate_mesh.setMeshData(meshdata=dv_plate_md)

    def get_atlas_angles(self):
        c_ang = (self.crotation_ctrl.h_spinbox.value(), self.crotation_ctrl.v_spinbox.value())
        s_ang = (self.srotation_ctrl.h_spinbox.value(), self.srotation_ctrl.v_spinbox.value())
        h_ang = (self.hrotation_ctrl.h_spinbox.value(), self.hrotation_ctrl.v_spinbox.value())
        return [c_ang, s_ang, h_ang]

    def set_volume_atlas_ctrl_data(self, atlas_ctrl_data):
        self.cpage_ctrl.page_slider.setValue(atlas_ctrl_data['coronal_index'])
        self.spage_ctrl.page_slider.setValue(atlas_ctrl_data['sagittal_index'])
        self.hpage_ctrl.page_slider.setValue(atlas_ctrl_data['horizontal_index'])
        atlas_rotation = atlas_ctrl_data['slice_rotation']
        self.crotation_ctrl.h_spinbox.setValue(atlas_rotation[0][0])
        self.crotation_ctrl.v_spinbox.setValue(atlas_rotation[0][1])
        self.srotation_ctrl.h_spinbox.setValue(atlas_rotation[1][0])
        self.srotation_ctrl.v_spinbox.setValue(atlas_rotation[1][1])
        self.hrotation_ctrl.h_spinbox.setValue(atlas_rotation[2][0])
        self.hrotation_ctrl.v_spinbox.setValue(atlas_rotation[2][1])

    def clear_atlas_stacks(self):

        valid_keys = ['atlas-overlay', 'atlas-contour', 'atlas-mask', 'circle_follow', 'lasso_path', 'atlas-virus',
                      'atlas-probe', 'atlas-cells', 'atlas-drawing']

        for da_key in valid_keys:
            self.working_atlas.image_dict[da_key].clear()

    def clear_atlas(self):
        self.cimg.img.clear()
        self.simg.img.clear()
        self.himg.img.clear()

    def get_coronal_3d(self, points2, coronal_index=None):
        if coronal_index is None:
            da_y = np.ones(len(points2)) * self.current_coronal_index
        else:
            da_y = coronal_index
        points3 = np.vstack([points2[:, 0], da_y, self.atlas_size[0] - points2[:, 1]]).T
        points3 = points3 - self.origin_3d
        if self.coronal_rotated:
            rot_mat = self.c_rotm_3d
            rotation_origin = self.rotate_origin_3d
            points3 = np.dot(rot_mat, (points3 - rotation_origin).T).T + rotation_origin
            print('p3', points3)

        return points3

    def get_sagital_3d(self, points2, sagital_index=None):
        if sagital_index is None:
            da_x = np.ones(len(points2)) * self.current_sagital_index
        else:
            da_x = sagital_index
        points3 = np.vstack([da_x, points2[:, 0], self.atlas_size[0] - points2[:, 1]]).T
        points3 = points3 - self.origin_3d
        if self.sagital_rotated:
            rot_mat = self.s_rotm_3d
            rotation_origin = self.rotate_origin_3d
            points3 = np.dot(rot_mat, (points3 - rotation_origin).T).T + rotation_origin
        return points3

    def get_horizontal_3d(self, points2, horizontal_index=None):
        if horizontal_index is None:
            da_z = np.ones(len(points2)) * self.current_horizontal_index
        else:
            da_z = horizontal_index
        points3 = np.vstack([points2[:, 1], points2[:, 0], self.atlas_size[0] - da_z]).T
        points3 = points3 - self.origin_3d
        if self.horizontal_rotated:
            rot_mat = self.h_rotm_3d
            rotation_origin = self.rotate_origin_3d
            points3 = np.dot(rot_mat, (points3 - rotation_origin).T).T + rotation_origin
        return points3

    def get_3d_pnts(self, processing_data, atlas_display):
        if atlas_display == 'coronal':
            print(processing_data)
            data = self.get_coronal_3d(processing_data)
            print(data)
        elif atlas_display == 'sagittal':
            data = self.get_sagital_3d(processing_data)
        else:
            data = self.get_horizontal_3d(processing_data)
        return data

    def get_pre_np2_data(self, data, atlas_display, site_face):
        points3_list = []
        base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
        if atlas_display == 'coronal':
            if site_face == 0:
                start_pnt, end_pnt = rotate_base_points(data, base_loc)
                for i in range(4):
                    points2 = np.vstack([start_pnt[i], end_pnt[i]])
                    p3 = self.get_coronal_3d(points2)
                    points3_list.append(p3)
            else:
                for i in range(4):
                    points2 = data.copy()
                    coronal_index = np.ones(2) * (self.current_coronal_index + base_loc[i])
                    p3 = self.get_coronal_3d(points2, coronal_index)
                    points3_list.append(p3)
        elif atlas_display == 'sagittal':
            if site_face == 0:
                start_pnt, end_pnt = rotate_base_points(data, base_loc)
                for i in range(4):
                    points2 = np.vstack([start_pnt[i], end_pnt[i]])
                    p3 = self.get_sagital_3d(points2)
                    points3_list.append(p3)
            else:
                for i in range(4):
                    points2 = data.copy()
                    sagital_index = np.ones(2) * (self.current_sagital_index + base_loc[i])
                    p3 = self.get_sagital_3d(points2, sagital_index)
                    points3_list.append(p3)
        else:
            if site_face == 0:
                start_pnt, end_pnt = rotate_base_points(data, base_loc)
                for i in range(4):
                    points2 = np.vstack([start_pnt[i], end_pnt[i]])
                    p3 = self.get_horizontal_3d(points2)
                    points3_list.append(p3)
            else:
                for i in range(4):
                    points2 = data.copy()
                    horizontal_index = np.ones(2) * (self.current_horizontal_index + base_loc[i])
                    p3 = self.get_horizontal_3d(points2, horizontal_index)
                    points3_list.append(p3)
        return points3_list

    def pre_trajectory_changed(self):
        for i in range(4):
            self.working_atlas.pre_trajectory_list[i].clear()

    #
    def get_pre_coronal_np2_data(self, data, site_face):
        base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
        if site_face == 0:
            start_pnt, end_pnt = rotate_base_points(data, base_loc)
            self.anchor_coronal_index = None
            for i in range(4):
                da_pnts = np.asarray([start_pnt[i], end_pnt[i]])
                self.working_atlas.pre_trajectory_list[i].setData(da_pnts)
            temp = np.vstack([start_pnt, end_pnt])
            self.working_atlas.image_dict['atlas-probe'].setData(pos=temp)
        else:
            start_pnt = data[0]
            end_pnt = data[1]
            self.working_atlas.pre_trajectory_list[0].setData(data)
            self.anchor_coronal_index = base_loc + self.current_coronal_index
        return start_pnt, end_pnt

    #
    def get_pre_sagital_np2_data(self, data, site_face):
        base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
        if site_face == 0:
            start_pnt, end_pnt = rotate_base_points(data, base_loc)
            self.anchor_sagital_index = None
            for i in range(4):
                da_pnts = np.asarray([start_pnt[i], end_pnt[i]])
                self.working_atlas.pre_trajectory_list[i].setData(da_pnts)
            temp = np.vstack([start_pnt, end_pnt])
            self.working_atlas.image_dict['atlas-probe'].setData(pos=temp)
        else:
            start_pnt = data[0]
            end_pnt = data[1]
            self.working_atlas.pre_trajectory_list[0].setData(data)
            self.anchor_sagital_index = base_loc + self.current_sagital_index
        return start_pnt, end_pnt

    #
    def get_pre_horizontal_np2_data(self, data, site_face):
        base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
        if site_face == 0:
            start_pnt, end_pnt = rotate_base_points(data, base_loc)
            self.anchor_horizontal_index = None
            for i in range(4):
                da_pnts = np.asarray([start_pnt[i], end_pnt[i]])
                self.working_atlas.pre_trajectory_list[i].setData(da_pnts)
            temp = np.vstack([start_pnt, end_pnt])
            self.working_atlas.image_dict['atlas-probe'].setData(pos=temp)
        else:
            start_pnt = data[0]
            end_pnt = data[1]
            self.working_atlas.pre_trajectory_list[0].setData(data)
            self.anchor_horizontal_index = base_loc + self.current_horizontal_index
        return start_pnt, end_pnt

    #
    def draw_volume_pre_trajectory(self, data, n_pre_trajectory):
        if len(data) == 1:
            if n_pre_trajectory == 1:
                self.working_atlas.image_dict['atlas-probe'].setData(pos=np.asarray(data))
            else:
                base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
                temp = np.stack([data[0][0] + base_loc, np.repeat(data[0][1], 4)], axis=1)
                self.working_atlas.image_dict['atlas-probe'].setData(pos=np.asarray(temp))
        elif len(data) == 2:
            if n_pre_trajectory == 1:
                print('hahahahah')
                self.working_atlas.image_dict['atlas-probe'].setData(pos=np.asarray(data))
            else:
                print('sdfasd')
                base_loc = np.array([-375, -125, 125, 375]) / self.vox_size_um
                start_pnt, end_pnt = rotate_base_points(np.asarray(data), base_loc)
                temp = np.vstack([start_pnt, end_pnt])
                self.working_atlas.image_dict['atlas-probe'].setData(pos=temp)
        else:
            self.working_atlas.image_dict['atlas-probe'].clear()






