import os
import json
import functools
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader
import PySide6.QtWidgets as QT
from PySide6.QtGui import QIcon, QColor, QMovie
import maya.cmds as cmds
from shiboken6 import wrapInstance
from maya import OpenMayaUI as omui


#main_window_method to parent UI
def get_maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QWidget)


class ControlButton(QPushButton):
    def __init__(self, name, file_path, icon_path=None, delete_callback=None):
        super(ControlButton, self).__init__(name)
        self.name = name
        self.file_path = file_path
        self.icon_path = icon_path
        self.delete_callback = delete_callback

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

    def open_menu(self, pos):
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == delete_action:
            self.confirm_and_delete()

    def confirm_and_delete(self):
        confirm = QMessageBox.question(
            self,
            "Delete Control",
            f"Delete '{self.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if self.file_path and os.path.exists(self.file_path):
                os.remove(self.file_path)
            if self.icon_path and os.path.exists(self.icon_path):
                os.remove(self.icon_path)
            if self.delete_callback:
                self.delete_callback(self)

class Draw:
    def __init__(self, curve=None):
        self.curve = curve
        if curve:
            self.curve = curve
        elif len(cmds.ls(selection=True)):
            self.curve = cmds.ls(selection=True)[0]

    def get_cv_positions(self, curve, cv_len):
        cv_pose = []
        for i in range(cv_len):
            pos = cmds.xform(f'{curve}.cv[{i}]', query=True, objectSpace=True, translation=True)
            cv_pose.append(pos)
        return cv_pose

    def get_curve_info(self, curve=None):
        if not curve:
            curve = self.curve
        self.curve_dict = {}
        for crv in cmds.listRelatives(curve, shapes=True, fullPath=True):
            spans = cmds.getAttr(crv + '.spans')
            degree = cmds.getAttr(crv + '.degree')
            form = cmds.getAttr(crv + '.form')
            cv_len = len(cmds.ls(crv + '.cv[*]', flatten=True))
            cv_pose = self.get_cv_positions(crv, cv_len)

            curve_info = {
                'spans': spans,
                'degree': degree,
                'form': form,
                'cv_len': cv_len,
                'cv_pos': cv_pose,
                'tag': 'default'
            }
            self.curve_dict[crv] = curve_info
        return self.curve_dict

    def write_curve(self, name=None, force=True, tag="default"):
        if not self.curve:
            cmds.error('No curve selected.')

        if not name:
            name = self.curve

        curve_data = self.get_curve_info(self.curve)
        for data in curve_data.values():
            data['tag'] = tag

        json_path = os.path.join(SHAPE_DIR, f"{name}.json")

        if os.path.isfile(json_path) and not force:
            cmds.error(f"Curve {name} already exists. Use force=True to overwrite.")

        with open(json_path, 'w') as f:
            json.dump(curve_data, f, indent=4)

    def create_curve(self, name='default', shape='circle', scale=1.0):
        file_path = os.path.join(SHAPE_DIR, f"{shape}.json")
        if not os.path.isfile(file_path):
            cmds.error(f"No shape file found: {file_path}")

        with open(file_path, 'r') as f:
            curve_dict = json.load(f)

        for i, (shp, info) in enumerate(curve_dict.items()):
            points = [[p * scale for p in pt] for pt in info['cv_pos']]
            if i == 0:
                self.curve = cmds.curve(point=points, degree=info['degree'], name=name)
            else:
                tmp = cmds.curve(point=points, degree=info['degree'])
                shape = cmds.listRelatives(tmp, shapes=True)[0]
                cmds.parent(shape, self.curve, shape=True, relative=True)
                cmds.delete(tmp)

            if info['form'] >= 1:
                shape_nodes = cmds.listRelatives(self.curve, shapes=True, fullPath=True)
                for shape_node in shape_nodes:
                    if cmds.getAttr(f"{shape_node}.form") == 0:
                        cmds.closeCurve(shape_node, ch=False, ps=0, rpo=True)

        cmds.select(cl=True)
        return self.curve


class ControlLoader:
    def __init__(self, scroll_layout, icon_dir):
        # def __init__(self, scroll_layout, icon_dir, color_manager):
        self.scroll_layout = scroll_layout
        self.icon_dir = icon_dir
        # self.color_manager = color_manager
        self.selected_color = (1.0, 1.0, 0.0) 
        self.preset_colors = [
            (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0),
            (1.0, 1.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)
        ]

        self.ctrlscalevalue = 1.0
        self.prefix = None
        self.curvename = None
        self.suffix = None
        
        #column resize button storage
        self.control_buttons = []

        # offset grp state
        self.addOffset = False
        # axis to affect the direction the curve is pointing
        self.axis = "Y"
        self.axis_rotation = {
            "X": (0, 0, -90),
            "Y": (0, 0, 0),
            "Z": (90, 0, 0),
        }
        delete_callback = None
        self.delete_callback = delete_callback
                        
    def get_color_style(self, color_tuple):
        r, g, b = [int(c * 255) for c in color_tuple]
        return f"background-color: rgb({r}, {g}, {b}); border: 1px solid gray;"

    def get_color_tooltip(self, color_tuple):
        r, g, b = [int(c * 255) for c in color_tuple]
        return f"RGB: {r}, {g}, {b}"

    def scalevalue(self, value):
        self.ctrlscalevalue = value
        #print('scale value is updating')
        print(self.ctrlscalevalue)

    def add_color_swatch(self, color):
        self.swatch_style = self.get_color_style(color)  
        self.swatch_tooltip = self.get_color_tooltip(self.selected_color)
        self.extraswatch_style = """
                border-radius: 2px;
            }
            QFrame:hover {
                border: 1px solid #888;
            """
        self.color_swatch = QLabel() 
        self.color_swatch.setFixedSize(40, 20)
        self.color_swatch.setStyleSheet(self.swatch_style + self.extraswatch_style)
        self.color_swatch.setToolTip(self.swatch_tooltip)
        self.pickcolorlayout.addWidget(self.color_swatch)

        for color in self.preset_colors:
            self.swatch = QPushButton()
            self.swatch.setFixedSize(12, 12)
            base_presetstyle = self.get_color_style(color)
            extra_style = """
                border-radius: 6px;
                min-width: 10px;
                min-height: 10px;
            }
            QFrame:hover {
                border: 2px solid #888;
                background-color: rgba(255, 255, 255, 30);
            """

            # self.swatch.setStyleSheet(self.get_color_style(color))
            self.swatch.setStyleSheet(base_presetstyle + extra_style)
            self.swatch.clicked.connect(functools.partial(self.set_color_from_preset, color))
            self.swatch.clicked.connect(functools.partial(self.set_color_from_preset, color))

            self.presetcolorlayout.addWidget(self.swatch)

    def set_color_from_preset(self, color_tuple):
        self.selected_color = color_tuple
        self.color_swatch.setStyleSheet(self.get_color_style(color_tuple) + self.extraswatch_style)
        self.color_swatch.setToolTip(self.get_color_tooltip(color_tuple))
        # self.color_manager = color_manager



    def save_selected(self):
        if not cmds.ls(selection=True):
            cmds.warning("No curve to save selected.")
            return
        name = cmds.ls(selection=True)[0]
        #
        sel_shape = cmds.listRelatives(name, shapes=True, fullPath=True)
        sel_shaper = sel_shape[0]
        curvepos = cmds.xform(name, q=True, ws=True, rp=True)
        cmds.select(cl=True)
        tmp_grp = cmds.group(empty=True, name='tmp_grp')
        cmds.delete(cmds.parentConstraint(name, tmp_grp))
        for shape in sel_shape:
            dup_transform = cmds.duplicate(shape, name=shape.split('|')[-1] + "_dup")[0]
            dup_shapes = cmds.listRelatives(dup_transform, shapes=True, fullPath=True) or []
            
            for dup_shape_node in dup_shapes:
                cmds.parent(dup_shape_node, tmp_grp, shape=True, relative=True)
            
            cmds.delete(dup_transform)
            
        cmds.setAttr(f"{tmp_grp}.translate", 0, 0, 0)
        cmds.setAttr(f"{tmp_grp}.rotate", 0, 0, 0)
        cmds.setAttr(f"{tmp_grp}.scale", 1, 1, 1)
                
        
        draw = Draw(tmp_grp)
        draw.write_curve(name=name, force=True)
        cmds.inViewMessage(amg=f'Saved control: <hl>{name}</hl>', pos='topCenter', fade=True)
        cmds.delete(tmp_grp)
        self.load_controls()

    def load_controls(self):
        columns = 3
        control_files = [f for f in os.listdir(SHAPE_DIR) if f.endswith(".json")]
        default_icon_path = os.path.join(self.icon_dir, "default.png")

        if not os.path.exists(default_icon_path):
            print(f"Warning: No default icon at {default_icon_path}.")
            default_icon = QIcon()
        else:
            default_icon = QIcon(default_icon_path)

        for index, file in enumerate(control_files):
            name = os.path.splitext(file)[0]
            self.name = os.path.splitext(file)[0]
            file_path = os.path.join(SHAPE_DIR, file)
            with open(file_path, 'r') as f:
                data = json.load(f)

            row = index // columns
            col = index % columns
            icon_path = os.path.join(self.icon_dir, f"{name}.png")
            btn = ControlButton(
                    name=name,
                    file_path=file_path,
                    icon_path=icon_path if os.path.exists(icon_path) else None,
                    delete_callback=self.remove_button
            )
            if os.path.exists(icon_path):
                btn_icon = QIcon(icon_path)
            else:
                btn_icon = default_icon

            btn.setIcon(btn_icon)
            btn.setIconSize(QSize(48, 48))

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: white;
                    text-align: center;
                    border: 2px solid #333333;
                    border-radius: 0px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555555;
                    border: 2px solid #666666;
                    cursor: pointer;
                }
                QPushButton:pressed {
                    background-color: #333333;
                    border: 2px solid #444444;
                }
            """)
            btn.clicked.connect(functools.partial(self.create_control, name))
            
        

            self.control_buttons.append(btn)
            self.scroll_layout.addWidget(btn, row, col)
            self.parent_ui = self.scroll_layout.parent().parent()


        cmds.select(cl=True)

    def refresh_buttons(self):
        for btn in self.control_buttons:
            self.scroll_layout.removeWidget(btn)
            btn.deleteLater()
        self.control_buttons.clear()
        self.load_controls()
        
    def remove_button(self, btn):
        self.refresh_buttons()
            
    def set_prefix(self, prefixname):
        self.prefix = prefixname

    def set_name(self, name):
        self.curvename = name

    def set_suffix(self, suffix):
        self.suffix = suffix


    def create_control(self, name):
        cmds.undoInfo(openChunk=True)
        try:

            selected_objects = cmds.ls(selection=True)

            # come back to this if/not and work a way to not have to duplicate the draw command
            if not selected_objects:
                print('No object selected')
                draw = Draw()
                ctrl = draw.create_curve(name=name, shape=name)
                shapes = cmds.listRelatives(ctrl, shapes=True, fullPath=True)
                for shape in shapes:
                    cmds.setAttr(f"{shape}.overrideEnabled", 1)
                    cmds.setAttr(f"{shape}.overrideRGBColors", 1)
                    cmds.setAttr(f"{shape}.overrideColorRGB", *self.selected_color)
                control_points = cmds.ls(f"{ctrl}.cv[*]", flatten=True)
                cmds.scale(self.ctrlscalevalue, self.ctrlscalevalue, self.ctrlscalevalue, control_points, relative=True)
                return

            # selected_axis = self.get_selected_axis()
            draw = Draw()
            ctrl = draw.create_curve(name=name, shape=name)

            print('scale value in update class')
            print(self.ctrlscalevalue)
            #Assuming a single selection for simplicity
            selected_obj = selected_objects[0]
            obj_pos = cmds.xform(selected_obj, query=True, worldSpace=True, rp=True)
            obj_rot = cmds.xform(selected_obj, query=True, worldSpace=True, ro=True)
            control_points = cmds.ls(f"{ctrl}.cv[*]", flatten=True)
            cmds.scale(self.ctrlscalevalue, self.ctrlscalevalue, self.ctrlscalevalue, control_points, relative=True)
            cmds.xform(ctrl, worldSpace=True, translation=obj_pos)
            cmds.xform(ctrl, worldSpace=True, ro=obj_rot)
            
            #override curve color with the selected color from the picker
            shapes = cmds.listRelatives(ctrl, shapes=True, fullPath=True)
            for shape in shapes:
                cmds.setAttr(f"{shape}.overrideEnabled", 1)
                cmds.setAttr(f"{shape}.overrideRGBColors", 1)
                cmds.setAttr(f"{shape}.overrideColorRGB", *self.selected_color)
        except Exception as e:
            print("Error creating control:", e)
        finally:
            print(self.prefix, 'helloworld')
            # Axis orrientation Block ( Consider restructure/implementing a fail check)
            rot = self.axis_rotation[self.axis]
            if shapes:
                for shape in shapes:
                    cvs = cmds.ls(f"{shape}.cv[*]", flatten=True)
                    for cv in cvs:
                        cmds.rotate(rot[0], rot[1], rot[2], cv, relative=True, objectSpace=True)
            # Name setup for Control
            originalname = ctrl
            name_parts = []
            if hasattr(self, 'prefix') and self.prefix:
                name_parts.append(self.prefix.rstrip('_'))

            if hasattr(self, 'curvename') and self.curvename:
                name_parts.append(self.curvename)
            else:
                name_parts.append(originalname)

            if hasattr(self, 'suffix') and self.suffix:
                name_parts.append(self.suffix.lstrip('_'))

            ctrl = cmds.rename(ctrl, ("_".join(name_parts) if name_parts else self.name))

            # Implement NPO/Offset group
            if self.addOffset:
                offset_grp_name = f"{ctrl}_npo"
                offset_grp = cmds.group(empty=True, name=offset_grp_name)
                cmds.delete(cmds.parentConstraint(ctrl, offset_grp))
                cmds.parent(ctrl, offset_grp)
            cmds.undoInfo(closeChunk=True)


class ControlLibraryUI:
    def __init__(self, ui_file, icon_dir):
        self.ui_file = ui_file
        self.icon_dir = icon_dir
        self.ui = None
        # self.grid_layout = QGridLayout(self.scrollAreaWidgetContents)
        # self.scrollAreaWidgetContents.setLayout(self.grid_layout)
        self.load_ui()
        self.control_loader = ControlLoader(self, self.icon_dir)
        self.setup_ui()
        self.control_loader.scroll_layout = self.scroll_layout
        self.control_loader.load_controls()
        self.control_loader.add_color_swatch(self.control_loader.selected_color)

    
    def load_ui(self):
        ui_file = QFile(self.ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

    def setup_ui(self):
        #UI settings
        self.ui.setWindowTitle('CLib- Control Studio')
        self.ui.setParent(get_maya_main_window())
        # self.ui.setWindowFlags(self.ui.windowFlags() | Qt.WindowStaysOnTopHint)
        self.ui.setParent(get_maya_main_window())
        self.ui.setWindowFlags(Qt.Window)
        self.ui.setWindowIcon(QIcon(os.path.join(icon_dir, "ControlLib.png")))
        self.ui.resize(1000, 200)

        # Locate widgets
        groupbox_widget = self.ui.findChild(QGroupBox, "groupBox")
        namesetting_widget = self.ui.findChild(QGroupBox, "nameSetting_Grp")
        preset_color_Widget = self.ui.findChild(QWidget, "preset_color_Wdg")
        pick_color_Widget = self.ui.findChild(QWidget, "pick_color_Wdg")
        uiborder_R_widget = self.ui.findChild(QWidget, "widget_4")
        OffsetGrp_chck = self.ui.findChild(QCheckBox, "offsetgroup_Chck")
        leftborder_line = self.ui.findChild(QFrame, "line")
        leftborder_line2 = self.ui.findChild(QFrame, "line2")
        rightborder_line = self.ui.findChild(QFrame, "line")
        rightborder_dot1 = self.ui.findChild(QLabel, "label_4")
        rightborder_dot2 = self.ui.findChild(QLabel, "label_5")
        luckynote = self.ui.findChild(QLabel, "luckyNumber")
        self.scalelabel = self.ui.findChild(QLabel, "scale_Lbl")

        color_radiobutton = self.ui.findChild(QRadioButton, "colorradio")
        setup_radiobutton = self.ui.findChild(QRadioButton, "setupradio")
        # radiobutton_z = self.ui.findChild(QRadioButton, "radioButton")
        pickcolor_btn = self.ui.findChild(QPushButton, "pickColor_Btn")
        storecontrol_btn = self.ui.findChild(QPushButton, "pushButton_2")
        radiobutton_widget = self.ui.findChild(QWidget, "axis_Wdg")
        scaleLabel_widget = self.ui.findChild(QWidget, "ctrlscale_Wdg")
        scaleSlider_widget = self.ui.findChild(QWidget, "scaleSlider_Wdg")

        self.color_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
        self.setting_widget = self.ui.findChild(QStackedWidget, "stackedWidget_2")
        self.mainhubwidget = self.ui.findChild(QStackedWidget, "stackedWidget_3")

        self.prefixLineEdit = self.ui.findChild(QLineEdit, "PrefixLine")
        self.suffixLineEdit = self.ui.findChild(QLineEdit, "SuffixLine")
        self.nameLineEdit = self.ui.findChild(QLineEdit, "NameLine")

        self.prefixLineEdit.setPlaceholderText("Type a Prefix")
        self.suffixLineEdit.setPlaceholderText("Type a Suffix")
        self.nameLineEdit.setPlaceholderText("Name of Curve")
        self.testname = self.ui.findChild(QLabel, "demo_text")

        luckynote.setToolTip(
            "why IV? its just one of my favorite numbers :D, thanks for using my little tool, hope you like it and if it ever helps you down the line even better")
        luckynote.setStyleSheet("""
            QToolTip {
                background-color: #444444;
                color: #f0f0f0;
                border: 1px solid #888888;
                padding: 10px;
                font-size: 12px;
                font-family: Arial, sans-serif;
                border-radius: 5px;
                opacity: 0.9;
            }
        """)
        self.nameLineEdit.textChanged.connect(lambda: self.replace_invalid_chars(self.nameLineEdit))
        self.prefixLineEdit.textChanged.connect(lambda: self.replace_invalid_chars(self.prefixLineEdit))
        self.suffixLineEdit.textChanged.connect(lambda: self.replace_invalid_chars(self.suffixLineEdit))

        self.prefixLineEdit.textChanged.connect(self.generate_control_name)
        self.nameLineEdit.textChanged.connect(self.generate_control_name)
        self.suffixLineEdit.textChanged.connect(self.generate_control_name)

        # connect name settings LineWidgets to handle methods, sending each update to the ControlLoader
        self.prefixLineEdit.textChanged.connect(self.handle_prefix_changed)
        self.nameLineEdit.textChanged.connect(self.handle_name_changed)
        self.suffixLineEdit.textChanged.connect(self.handle_suffix_changed)

        self.prefixLineEdit.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #6a9fb5;
                background-color: #333333;
            }
        """)

        self.suffixLineEdit.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #6a9fb5;
                background-color: #333333;
            }
        """)

        self.nameLineEdit.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #6a9fb5;
                background-color: #333333;
            }
        """)

        # state check for offsetbtn connecting to update offset method
        OffsetGrp_chck.stateChanged.connect(self.update_offset_state)
        OffsetGrp_chck.setStyleSheet("""
        QCheckBox {
            spacing: 8px;
            font-size: 14px;
            color: #CCCCCC;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border-radius: 7px;
            border: 2px solid #888888;
        }

        QCheckBox::indicator:checked {
            background-color: #645d12;
            border: 2px solid #fed42b;
        }

        QCheckBox::indicator:unchecked:hover {
            border: 1px solid #888888;
        }

        QCheckBox::indicator:checked:hover {
            background-color: #fbd22c;
            border: 2px solid #cccccc;
        }
        """)
        # seetup layound for scale slider widget
        if not scaleSlider_widget.layout():
            scaleSlider_layout = QHBoxLayout(scaleSlider_widget)
            scaleSlider_widget.setLayout(scaleSlider_layout)
        else:
            scaleSlider_layout = scaleSlider_widget.layout()

        # seetup layound for scale label widget
        if not scaleLabel_widget.layout():
            scaleLabel_layout = QHBoxLayout(scaleLabel_widget)
            scaleLabel_widget.setLayout(scaleLabel_layout)
        else:
            scaleLabel_layout = scaleLabel_widget.layout()

        # seetup layound for XYZ radio button widget
        if not radiobutton_widget.layout():
            radiobutton_layout = QHBoxLayout(radiobutton_widget)
            radiobutton_widget.setLayout(radiobutton_layout)
        else:
            radiobutton_layout = radiobutton_widget.layout()

        self.radio_x = QRadioButton("X")
        self.radio_y = QRadioButton("Y")
        self.radio_z = QRadioButton("Z")

        radiobutton_layout.addWidget(self.radio_x)
        radiobutton_layout.addWidget(self.radio_y)
        radiobutton_layout.addWidget(self.radio_z)

        self.radio_x.toggled.connect(self.update_axis)
        self.radio_y.toggled.connect(self.update_axis)
        self.radio_z.toggled.connect(self.update_axis)
        self.radio_y.setChecked(True)


        #connect the top buttons to switch between color and attribute menu
        color_radiobutton.toggled.connect(lambda checked: self.set_page_if_checked(0, checked))
        setup_radiobutton.toggled.connect(lambda checked: self.set_page_if_checked(1, checked))

        color_radiobutton.setStyleSheet("""
            QRadioButton {
                spacing: 8px;
                color: #dddddd;
            }
            QRadioButton::indicator {
                border-radius: 7px;
                border: 2px solid #888888;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #444444;
                border: 2px solid #fed42b;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #cccccc;
            }
        """)

        setup_radiobutton.setStyleSheet("""
            QRadioButton {
                spacing: 8px;
                color: #dddddd;
            }
            QRadioButton::indicator {
                border-radius: 7px;
                border: 2px solid #888888;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #444444;
                border: 2px solid #fed42b;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #cccccc;
            }
        """)

        self.radio_x.setStyleSheet("""
            QRadioButton {
                spacing: 8px;
                color: #f4f4f4;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 12px;
                height: 12px;
                border-radius: 6px; /* half of width/height */
                border: 2px solid #888888;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #b6a344;
                border: 2px solid #fed42b;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #cccccc;
            }
        """)

        self.radio_y.setStyleSheet("""
            QRadioButton {
                spacing: 8px;
                color: #f4f4f4;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 12px;
                height: 12px;
                border-radius: 6px; /* half of width/height */
                border: 2px solid #888888;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #b6a344;
                border: 2px solid #fed42b;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #cccccc;
            }
        """)

        self.radio_z.setStyleSheet("""
            QRadioButton {
                spacing: 8px;
                color: #f4f4f4;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 12px;
                height: 12px;
                border-radius: 6px; /* half of width/height */
                border: 2px solid #888888;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #b6a344;
                border: 2px solid #fed42b;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #cccccc;
            }
        """)

        #Scale slider init
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(1)
        self.slider.setTickInterval(5)

        self.scalelabel.setText(f"Universal Scale:    {self.slider.value()}")
        # scaleLabel_layout.addWidget(self.label)
        scaleSlider_layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.update_label)
        self.slider.valueChanged.connect(lambda val: self.control_loader.scalevalue(val / 10.0))

        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #ccc;
                margin: 0 8px;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #555;
                border: none;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }

            QSlider::handle:horizontal:hover {
                background: #777;
            }

            QSlider::sub-page:horizontal {
                background: #ffd52b;
                border-radius: 3px;
            }

            QSlider::add-page:horizontal {
                background: #e0e0e0;
                border-radius: 3px;
            }
            """)

        self.scalelabel.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #dddddd;
                padding: 1px;
            }
        """)

        #connect the pick Color and Save Curve buttons
        pickcolor_btn.clicked.connect(self.pick_color)
        storecontrol_btn.clicked.connect(self.control_loader.save_selected)

        pickcolor_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #bdbdbd;   
                background-color: #c1c1c1;   
                color: black;                
                padding: 2px 5px;           
                font: bold 10pt;             
                border-radius: 5px;         
                hover: rgb(255, 255, 255);

            }
            QPushButton:hover {
                background-color: #ffee6f; 
                border: 1px solid #3c8e40;
            }
            QPushButton:pressed {
                background-color: #ffcc33; 
                border: 1.3px solid #d7a21b;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
                border: 1px solid #cccccc;
            }
        """)

        storecontrol_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #bdbdbd;   
                background-color: #c1c1c1;   
                color: black;                
                padding: 2px 5px;           
                font: bold 10pt;             
                border-radius: 5px;         
                hover: rgb(255, 255, 255);

            }
            QPushButton:hover {
                background-color: #ffee6f; 
                border: 1px solid #3c8e40;
            }
            QPushButton:pressed {
                background-color: #ffcc33; 
                border: 1.3px solid #d7a21b;
            }
            QPushButton:disabled {
                background-color: #e0e0e0; 
                color: #9e9e9e;
                border: 1px solid #cccccc;
            }
        """)

        # Set up layout for groupbox widget
        if not groupbox_widget.layout():
            groupboxlayout = QGridLayout(groupbox_widget)
            groupbox_widget.setLayout(groupboxlayout)
        else:
            groupboxlayout = groupbox_widget.layout()

        # seetup layound for colorpreset widget
        if not pick_color_Widget.layout():
            pickcolorlayout = QHBoxLayout(pick_color_Widget)
            pick_color_Widget.setLayout(pickcolorlayout)
        else:
            pickcolorlayout = pick_color_Widget.layout()

        # seetup layound for colorpreset widget
        if not preset_color_Widget.layout():
            presetcolorlayout = QHBoxLayout(preset_color_Widget)
            preset_color_Widget.setLayout(presetcolorlayout)
        else:
            presetcolorlayout = preset_color_Widget.layout()

        self.control_loader.pickcolorlayout = pickcolorlayout
        self.control_loader.presetcolorlayout = presetcolorlayout

        # Creating the scroll layout before using it in ControlLoader
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QGridLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        groupboxlayout.addWidget(scroll_area)
        scroll_area.setStyleSheet("background: #232323; border-radius: 8px;")
        scroll_content.setStyleSheet("background: #242424; border-radius: 8px;")
        self.scroll_layout.setVerticalSpacing(0)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_area.setMinimumWidth(170)
        scroll_content.setMinimumHeight(500)

        # group box style setting
        groupbox_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid white;
                border-radius: 7px;
            }
            QGroupBox:title {
                font-size: 14px;
                top: -1px;
            }
        """)

        # group box style setting
        namesetting_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid white;
                border-radius: 7px;
            }
            QGroupBox:title {
                font-size: 14px;
                top: -1px;
            }
        """)
        # radio button on by default
        color_radiobutton.setChecked(True)

    def pick_color(self):
        color = QColorDialog.getColor(parent=self.ui, title="Pick a custom Curve Color")
        if color.isValid():
            self.control_loader.selected_color = (color.redF(), color.greenF(), color.blueF())
            self.control_loader.color_swatch.setStyleSheet(self.control_loader.get_color_style(
                self.control_loader.selected_color) + self.control_loader.extraswatch_style)
            self.control_loader.color_swatch.setToolTip(
                self.control_loader.get_color_tooltip(self.control_loader.selected_color))

    def set_page_if_checked(self, index, checked):
        if checked:
            self.color_widget.setCurrentIndex(index)
            self.mainhubwidget.setCurrentIndex(index)
            self.setting_widget.setCurrentIndex(0 if index == 1 else 1)

    def replace_invalid_chars(self, line_edit):
        text = line_edit.text()
        new_text = text.replace(" ", "_")
        if text != new_text:
            line_edit.setText(new_text)

    def handle_prefix_changed(self, text):
        cleaned = text.replace(" ", "_")
        if text != cleaned:
            self.prefixLineEdit.setText(cleaned)
        self.control_loader.set_prefix(cleaned)

    def handle_name_changed(self, text):
        cleaned = text.replace(" ", "_")
        if text != cleaned:
            self.nameLineEdit.setText(cleaned)
        self.control_loader.set_name(cleaned)

    def handle_suffix_changed(self, text):
        cleaned = text.replace(" ", "_")
        if text != cleaned:
            self.suffixLineEdit.setText(cleaned)
        self.control_loader.set_suffix(cleaned)

    def generate_control_name(self):
        prefix = self.prefixLineEdit.text()
        name = self.nameLineEdit.text()
        suffix = self.suffixLineEdit.text()

        parts = [prefix, name, suffix]
        base_name = ''.join(part for part in parts if part)

        final_name = base_name
        # self.testname = final_name

        self.testname.setText(f"Preview: {final_name}")
        # return final_name

    def build_control_name(self, default_name):
        prefix = self.prefixEdit.text().strip()
        main = self.nameLineEdit.text().strip()
        suffix = self.suffixEdit.text().strip()

        # Use default name if main is empty
        main_name = main if main else default_name

        # Combine only non-empty parts
        name_parts = [prefix, main_name, suffix]
        full_name = "".join(part for part in name_parts if part)

        return full_name

    def update_axis(self):
        axis = self.get_selected_axis()
        self.control_loader.axis = axis

    #control primary axis with Y set as default
    def get_selected_axis(self):
        if self.radio_x.isChecked():
            return 'X'
        elif self.radio_y.isChecked():
            return 'Y'
        elif self.radio_z.isChecked():
            return 'Z'
        return 'Y' 

    def update_label(self, value):
        self.scalelabel.setText(f"Universal Scale:    {self.slider.value()}")

    def resizeEvent(self, event):
        print('all this time')
        super().resizeEvent(event)
        self.rebuild_control_layout()
    
    def rebuild_control_layout(self):
        if not hasattr(self, "scroll_layout") or not self.control_loader.control_buttons:
            return
    
        # Clear existing layout
        while self.control_loader.scroll_layout.count():
            child = self.control_loader.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
    
        # Compute column count based on width
        available_width = self.control_loader.scrollArea.viewport().width()
        button_width = 100  # Width + spacing estimate
        columns = max(1, available_width // button_width)
    
        for index, btn in enumerate(self.control_loader.control_buttons):
            row = index // columns
            col = index % columns
            self.control_loader.scroll_layout.addWidget(btn, row, col)
        
    # Update the control_loader addOffset value based on the checkbox.
    def update_offset_state(self, state):

        self.control_loader.addOffset = state == Qt.Checked

    def show(self):
        self.ui.show()


#Final UI init and Execution
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ui_file = os.path.join(SCRIPT_DIR, "ClibUI.ui")
SHAPE_DIR = os.path.join(SCRIPT_DIR, "shapes")
icon_dir = os.path.join(SCRIPT_DIR, "icons")
LOGO_PATH = os.path.join(icon_dir, "logo.gif")
# color_manager = ControlLoader()
control_ui = ControlLibraryUI(ui_file, icon_dir)


# my little launch animation
def show_splash():
    # global splash
    # splash_pix = QMovie(LOGO_PATH)
    # splash = QLabel()
    # splash.setMovie(splash_pix)
    # splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    # splash.setAlignment(Qt.AlignCenter)
    # splash.setAttribute(Qt.WA_TranslucentBackground)
    # splash.setStyleSheet("background-color: transparent;")
    # splash_pix.start()
    # splash.show()

    #QTimer.singleShot(800, continue_to_ui)
    continue_to_ui()


def continue_to_ui():
    splash.close()
    control_ui.show()


show_splash()