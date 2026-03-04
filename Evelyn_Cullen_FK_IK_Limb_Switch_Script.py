import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from maya.api import OpenMaya
from shiboken2 import wrapInstance 
"""
Evelyn Cullen
evelynemese@gmail.com

"""
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class FkIkSwitchWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        self.setObjectName("FKIK_limb_creator")
        self.setWindowTitle("FK IK Switch Creator")
        self.setMinimumWidth(40)
        self.setMaximumHeight(500)

        # Controller for switch
        self.switch_label  = QtWidgets.QLabel("Controller with FK IK switch attribute:")
        self.controller_name_input = QtWidgets.QLineEdit()
        self.use_selected_ctrl_btn = QtWidgets.QPushButton("Set to selected controller")
        self.use_selected_ctrl_btn.setToolTip("Sets the attribute controller to the current selected item")
        self.use_selected_ctrl_btn.clicked.connect(self.getSelectedCtrl)

        self.splitter = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        # Setting joints for switch
        self.leg_name = QtWidgets.QLineEdit(readOnly = True)
        self.set_leg_btn = QtWidgets.QPushButton("Set Leg")
        self.set_leg_btn.clicked.connect(lambda: self.setJoints(ui_element= self.leg_name))

        self.set_knee_btn = QtWidgets.QPushButton("Set Knee")
        self.knee_name = QtWidgets.QLineEdit(readOnly = True)
        self.set_knee_btn.clicked.connect(lambda: self.setJoints(ui_element= self.knee_name))

        self.set_ankle_btn = QtWidgets.QPushButton("Set Ankle")
        self.ankle_name = QtWidgets.QLineEdit(readOnly = True)
        self.set_ankle_btn.clicked.connect(lambda: self.setJoints(ui_element= self.ankle_name))

        self.set_foot_btn = QtWidgets.QPushButton("Set Foot")
        self.foot_name = QtWidgets.QLineEdit(readOnly = True)
        self.set_foot_btn.clicked.connect(lambda: self.setJoints(ui_element= self.foot_name))

        self.set_switch_joints_btn = QtWidgets.QPushButton("Set joints to current selection", self)
        self.set_switch_joints_btn.clicked.connect(lambda: self.setJoints(ui_element= [self.leg_name, self.knee_name, self.ankle_name, self.foot_name], multiple= True))

        # Create switch  button
        self.create_switch_btn = QtWidgets.QPushButton("Create Switch on Selected Joints", self)
        self.create_switch_btn.setStyleSheet("background-color: #5f9469; color: white; padding: 12px;")
        self.create_switch_btn.setMinimumHeight(60)
        self.create_switch_btn.clicked.connect(self.fk_ik)
        self.create_switch_btn.setToolTip("Creates an FK IK switch from selected joints. Joints need to be selected in hireachy order.")
        
        # Add Layout and Button to Window
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.switch_label)
        layout.addWidget(self.controller_name_input)
        layout.addWidget(self.use_selected_ctrl_btn)
        layout.addItem(self.splitter)

        #FK IK Switch
        leg_layout = QtWidgets.QHBoxLayout(self)
        leg_layout.addWidget(self.leg_name)
        leg_layout.addWidget(self.set_leg_btn)
        layout.addLayout(leg_layout)

        knee_layout = QtWidgets.QHBoxLayout(self)
        knee_layout.addWidget(self.knee_name)
        knee_layout.addWidget(self.set_knee_btn)
        layout.addLayout(knee_layout)

        ankle_layout = QtWidgets.QHBoxLayout(self)
        ankle_layout.addWidget(self.ankle_name)
        ankle_layout.addWidget(self.set_ankle_btn)
        layout.addLayout(ankle_layout)

        foot_layout = QtWidgets.QHBoxLayout(self)
        foot_layout.addWidget(self.foot_name)
        foot_layout.addWidget(self.set_foot_btn)
        layout.addLayout(foot_layout)

        layout.addWidget(self.set_switch_joints_btn)

        layout.addWidget(self.create_switch_btn)
        self.setLayout(layout)
         
    def fk_ik(self, *args):
        joint_set_list = [self.leg_name.text(), self.knee_name.text(), self.ankle_name.text(), self.foot_name.text()]
        print(self.controller_name_input.text())
        for joint in joint_set_list:
            if joint == "":
                FkIkLimbCreator(self.controller_name_input.text())
                return
        FkIkLimbCreator(self.controller_name_input.text(), joint_set_list)

    def getSelectedCtrl(self):
        ctrl = cmds.ls(selection = True, long = True)[0]
        self.controller_name_input.setText(ctrl)

    def setJoints(self, ui_element, multiple = False):
        user_selection = cmds.ls(selection = True)

        if multiple:
            if not user_selection:
                for ui in ui_element:
                    ui.setText("")

            for i in range(0, len(user_selection)):
                ui_element[i].setText(user_selection[i])
                if i > len(ui_element) - 1:
                    return

        else: 
            if not user_selection:
                ui_element.setText("")
            ui_element.setText(user_selection[0])
            
    def showWindow(*args):
        maya_main = maya_main_window() #Get the main window inside Maya
        
        # Check if window with this name already exists and delete it
        existing_window = maya_main.findChild(QtWidgets.QDialog, "HelloQtWindow")
        if existing_window:
            existing_window.close()
            existing_window.deleteLater()

        #Actually define the class and show it. It will come with show because of its super()
        window = FkIkSwitchWindow()
        window.show()
        return window

mywindow = FkIkSwitchWindow()
mywindow.showWindow()

def FkIkLimbCreator(user_input_ctrl_name = "", selected_jnts = ""):
    """
    FK IK limb creation tool
     Select 3 joints, if it's a leg. If 4 joints, it's an arm
     Order should be shoulder, elbow, wrist and hand OR leg, knee, ankle and foot
     need to be named beforehand

     arguments:
        user_input_ctrl_name = The control that the FK IK switch attribute will be added to 
    """
    
    # -------- Get selected joints
    print(selected_jnts)
    if not selected_jnts:
        selected_jnts = cmds.ls(selection=True, long = True)
    print(f"Selected joints are: {selected_jnts}")
    if len(selected_jnts) != 4:
        cmds.error("You need to select 4 joints in hierarchy order", n=True)

    # -------- Define switch attribute object
    if user_input_ctrl_name == "":
        switch_attr_obj = cmds.circle(name = "IK FK switch ctrl")[0]
    else:
        if cmds.objExists(user_input_ctrl_name):
            switch_attr_obj = user_input_ctrl_name
        else:
            cmds.error("The controller set for the FK IK switch attribute doesn't exist", n=True)
    
    # -------- Duplicate joints into FK and IK chain

    fk_jnts = []
    ik_jnts = []

    prev_ik = ""
    prev_fk = ""

    for index in range(0, len(selected_jnts)):
        #naming shenanigans

        acceptable_prefix = ["L", "R", "l", "r"]
        prefix = ""
        suffix = "_jnt"

        #Splits the joint name into suffix and the rest of the name
        basename_list = selected_jnts[index].split("|")[-1].split("_", 1)
        basename_list[-1] = basename_list[-1].replace("_bnd", "")


        for current_prefix in acceptable_prefix:
            if current_prefix == basename_list[0]:
                prefix  = current_prefix

        if prefix == "":
            basename = "_".join(basename_list).replace(suffix, "")
        else:
            basename = basename_list[-1].replace(suffix, "")


        #duplicate joint
        fk_jnt = cmds.duplicate(selected_jnts[index], parentOnly = True)
        ik_jnt = cmds.duplicate(selected_jnts[index], parentOnly = True)

        print(suffix)
        fk_jnt = cmds.rename(fk_jnt, prefix + "_FK_" + basename + suffix)
        ik_jnt = cmds.rename(ik_jnt, prefix + "_IK_" + basename + suffix)

        fk_jnts.append(fk_jnt)
        ik_jnts.append(ik_jnt)
        cmds.setAttr(f"{ik_jnt}.visibility", False)
        cmds.setAttr(f"{fk_jnt}.visibility", False)

        if prev_fk != "":
            cmds.parent(fk_jnt, prev_fk)
            cmds.parent(ik_jnt, prev_ik)

        prev_ik = ik_jnt
        prev_fk = fk_jnt
        print(suffix)


    # -------- Constrain base chain between fk and ik chain
    jnt_constraints = []
    for index in range(0, len(selected_jnts)):
        jnt_constraints.append(cmds.parentConstraint(fk_jnts[index], ik_jnts[index], selected_jnts[index], mo=False)[0])
    
    # -------- Create fk controls and constraints
    parent_ctrl = ""
    fk_ctrls = []
    for fk_jnt in fk_jnts:
        location = cmds.getAttr(f"{fk_jnt}.translate")[0]
        temp_ctrl = cmds.circle(name = fk_jnt.replace("_jnt", "_ctrl"))[0]
        temp_grp = cmds.group(temp_ctrl, name = fk_jnt.replace("_jnt", "_grp"))
        temp_constraint = cmds.parentConstraint(fk_jnt, temp_grp, mo=False)
        cmds.delete(temp_constraint)
        cmds.parentConstraint(temp_ctrl, fk_jnt)
        
        #Sets up the hierachy
        if parent_ctrl:
            cmds.parent(temp_grp, parent_ctrl)  
        parent_ctrl = temp_ctrl
        fk_ctrls.append(temp_ctrl)
    
    # -------- Create IK constraint for knee
    
    knee_ik_handle = cmds.ikHandle(sj = ik_jnts[0], ee = ik_jnts[2], name = prefix + basename + "_ikHandle")[0]
    leg_ik_ctrl = cmds.curve( degree = 1, knot = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], point = [(-0.5, 0.5, -0.5),(-0.5, 0.5, 0.5),(0.5, 0.5, 0.5),(0.5, 0.5, -0.5),(-0.5, 0.5, -0.5),(-0.5, -0.5, -0.5),(-0.5, -0.5, 0.5),(0.5, -0.5, 0.5),(0.5, 0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5)], name = prefix + "_IK_leg_ctrl")
    leg_ik_grp = cmds.group(leg_ik_ctrl, name= prefix + "_IK_leg_grp")
    temp_constraint = cmds.parentConstraint(knee_ik_handle, leg_ik_grp, mo=False)
    cmds.delete(temp_constraint)
    cmds.parent(knee_ik_handle, leg_ik_ctrl)
    cmds.setAttr(f"{knee_ik_handle}.visibility", False)
    
    # -------- Create IK constraint for foot
    foot_ik_handle = cmds.ikHandle(sj = ik_jnts[2], ee = ik_jnts[3],  solver = "ikSCsolver", name = prefix + basename + "_foot_ikHandle")[0]
    cmds.parent(foot_ik_handle, leg_ik_ctrl)
    cmds.setAttr(f"{foot_ik_handle}.visibility", False)
    
    # set up IK pole vector
    pole_vector_ctrl = cmds.circle(name = prefix + basename + "_polevector_ctrl")[0]
    pole_vector_grp = cmds.group(pole_vector_ctrl, name= prefix + "_polevector_grp")
    place_pole_vector_ctrl(
    start= ik_jnts[0],
    mid=ik_jnts[1],
    end=ik_jnts[2],
    pv_ctrl=pole_vector_grp,
    shift_factor=8,
    )
    cmds.poleVectorConstraint(pole_vector_ctrl, knee_ik_handle)

    # -------- Set up variable to control constraint and controller visbility 
    
    cmds.select(switch_attr_obj)
    print(switch_attr_obj)
    
    fk_ik_switch = prefix + "_Leg_FK_IK_Switch"
    cmds.addAttr(longName = fk_ik_switch, shortName = prefix + "_FK_IK", at = "float", minValue = 0, maxValue = 1, defaultValue = 0, keyable = True)
    print("Attribute added") 
    
    for index in range(0, len(jnt_constraints)):
        fk_weight_name = fk_jnts[index] + "W0"
        ik_weight_name = ik_jnts[index] + "W1"
        
        # Switch FK
        cmds.setAttr(f"{switch_attr_obj}.{fk_ik_switch}", 0)
        cmds.setAttr(f"{jnt_constraints[index]}.{fk_weight_name}", 1)
        cmds.setAttr(f"{jnt_constraints[index]}.{ik_weight_name}", 0)
        cmds.setAttr(f"{fk_ctrls[index]}.visibility", True)
        cmds.setAttr(f"{leg_ik_ctrl}.visibility", False)
        cmds.setAttr(f"{pole_vector_ctrl}.visibility", False)
        
        cmds.setDrivenKeyframe(f"{jnt_constraints[index]}.{fk_weight_name}", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{jnt_constraints[index]}.{ik_weight_name}", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{fk_ctrls[index]}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{leg_ik_ctrl}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{pole_vector_ctrl}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        
        # Switch IK
        cmds.setAttr(f"{switch_attr_obj}.{fk_ik_switch}", 1)
        cmds.setAttr(f"{jnt_constraints[index]}.{fk_weight_name}", 0)
        cmds.setAttr(f"{jnt_constraints[index]}.{ik_weight_name}", 1)
        cmds.setAttr(f"{fk_ctrls[index]}.visibility", False)
        cmds.setAttr(f"{leg_ik_ctrl}.visibility", True)
        cmds.setAttr(f"{pole_vector_ctrl}.visibility", True)
    
    
        cmds.setDrivenKeyframe(f"{jnt_constraints[index]}.{fk_weight_name}", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{jnt_constraints[index]}.{ik_weight_name}", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{fk_ctrls[index]}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{leg_ik_ctrl}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")
        cmds.setDrivenKeyframe(f"{pole_vector_ctrl}.visibility", cd = f"{switch_attr_obj}.{fk_ik_switch}")





"""
 Pole vector code is by Mischa Kolbe

"""


def get_pos_as_mvector(node):
    """Get a transform position as an MVector instance.
 
    Args:
        node (str): Name of transform.
 
    Returns:
        MVector: Position of given transform node.
    """
    pos = cmds.xform(node, query=True, translation=True, worldSpace=True)
    return OpenMaya.MVector(pos)
 
 
def place_pole_vector_ctrl(pv_ctrl, start, mid, end, shift_factor=2):
    """Position and orient the given poleVector control to avoid popping.
 
    Args:
        pv_ctrl (str): Name of transform to be used as poleVector.
        start (str): Name of start joint.
        mid (str): Name of mid joint.
        end (str): Name of end joint.
        shift_factor (float): How far ctrl should be moved away from mid joint.
    """
    # Find mid-point between start and end joint
    start_pos = get_pos_as_mvector(start)
    end_pos = get_pos_as_mvector(end)
    center_pos = (start_pos + end_pos) / 2
     
    # Use vector from mid-point to mid joint...
    mid_pos = get_pos_as_mvector(mid)

    offset = mid_pos - center_pos
    # ...to place the poleVector control
    pv_pos = center_pos + offset * shift_factor
    cmds.xform(pv_ctrl, translation=pv_pos, worldSpace=True)
 
    # Orient ctrl so that the XY-plane coincides with plane of joint chain.
    aim_constraint = cmds.aimConstraint(
        mid,
        pv_ctrl,
        aimVector=(1, 0, 0),
        upVector=(0, 1, 0),
        worldUpType="object",
        worldUpObject=start,
    )
    cmds.delete(aim_constraint)
    