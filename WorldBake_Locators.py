from maya import cmds
import maya.mel as mel 

class animWorldBakeLocators():
    def __init__(self):
        #Define window
        if cmds.window("bakeWindow", exists = True):
            cmds.deleteUI("bakeWindow")
            
        locBakeWindow = cmds.window("bakeWindow", title = "Animation World Bake Tool", widthHeight=(300, 200))
        
        cmds.columnLayout("masterLayout", rowSpacing = 5, columnWidth = 200)
        
        cmds.separator()
        
        self.smartBakeCheckbox = cmds.checkBox(l = "Smart Bake", v = False)
        
        cmds.button("controllerToLoc", h = 50, bgc = [0,0.5,0.5], l = "Bake Controllers to Locators", c = lambda x: self.bake_ctrl_to_loc(locScale = cmds.floatField(scaleField, q = True, value = True)))
        cmds.rowLayout("scaleLayout", numberOfColumns=2)
        cmds.text(label='Locator Scale:')
        scaleField = cmds.floatField(minValue = 0.01, maxValue = 1000, value = 1, precision = 2)

        cmds.separator(p = 'masterLayout')
        cmds.button("locatorToCont", h = 50,  bgc = [0,0,0.5], label = "Bake Locators to Controllers", c = self.bake_loc_to_ctrl, p = "masterLayout")
        
        cmds.showWindow(locBakeWindow)
        
    def bake_ctrl_to_loc(self, locScale, *args):
        """Bake animations from controls to new locators
            locScale = Float that determines scale of locators
        """
        # Containers
        locatorsList = []
        constraintsList = []
        
        # Timeline Info
        startTime = int(cmds.playbackOptions(q = True, minTime = True))
        endTime = int(cmds.playbackOptions(q = True, maxTime = True))
        
        # UserInfo
        smartBake = cmds.checkBox(self.smartBakeCheckbox, q = True, value = True)
        userSelection = cmds.ls(selection=True)
        

        # Error catches
        if len(userSelection) < 1:
            cmds.confirmDialog(title = "ERROR", message = "You don't have any objects selected")
            return
        for obj in userSelection:
            print(f"obj is {obj}")
            objShape = cmds.listRelatives(obj, s = True)
            print(f"shape is {objShape}")
            if cmds.nodeType(objShape) != "nurbsCurve":
                cmds.confirmDialog(title = "ERROR", message = "One or  more of your objects is not a curve")
                return
        
        # Baking
        for ctrl in userSelection:
            if ":" in ctrl:
                baseName = ctrl.split(":")[-1]
                locatorName = baseName + "__BAKED_LOCATOR_"
            else:
                locatorName = ctrl + "__BAKED_LOCATOR_"
                
            #if locScale
            bakedLocator = cmds.spaceLocator(name = locatorName)
            parentConst = cmds.parentConstraint(ctrl, bakedLocator, mo = False)
            cmds.setAttr(f"{locatorName}.scaleX", locScale)
            cmds.setAttr(f"{locatorName}.scaleY", locScale)
            cmds.setAttr(f"{locatorName}.scaleZ", locScale)

            locatorsList.append(bakedLocator[0])
            constraintsList.append(parentConst[0])   
        
        cmds.select(locatorsList, replace = True)
        cmds.bakeResults(time = (startTime, endTime), sr = (smartBake, 0), at = ("tx", "ty", "tz", "rx", "ry", "rz"))

        for constraint in constraintsList:
           cmds.delete(constraint)
        
        
    def bake_loc_to_ctrl(self, *args):
        """Bake animations from locators back to controls with the same name"""
        # Containers
        constraintsList = []
        locatorsList = []
        controlList = []
        failList = []
        failMessage = ""

        # Timeline Info
        startTime = int(cmds.playbackOptions(q = True, minTime = True))
        endTime = int(cmds.playbackOptions(q = True, maxTime = True))
        
        # User info
        userSelection = cmds.ls(selection=True)
        smartBake = cmds.checkBox(self.smartBakeCheckbox, q = True, value = True)
        
        # Error Catches
        if len(userSelection) < 1:
            cmds.confirmDialog(title = "ERROR", message = "Select control to bake")
            return
        for obj in userSelection:
            objShape = cmds.listRelatives(obj, s = True)
            if cmds.nodeType(objShape) != "nurbsCurve":
                cmds.confirmDialog(title = "ERROR", message = "One or  more of your objects is not a curve")
                return
                
        # Baking
        
        for ctrl in userSelection:
            if ":" in ctrl:
                ctrl_basename = ctrl.split(":")[-1]
                
            else:
                ctrl_basename = ctrl
                
            locator = ctrl_basename + "__BAKED_LOCATOR_"
            if cmds.objExists(locator):
                parentConst = cmds.parentConstraint(locator, ctrl, mo = False)
                constraintsList.append(parentConst)

                locatorsList.append(locator)
                controlList.append(ctrl)

            else:
                failList.append(ctrl)

        cmds.select(controlList)
        cmds.bakeResults(time = (startTime, endTime), sr = (smartBake, 0), at = ("tx", "ty", "tz", "rx", "ry", "rz"))
        
        for constraint in constraintsList:
            cmds.delete(constraint)
        for locator in locatorsList:
            cmds.delete(locator)
                
        if len(failList) > 0:
            for failObj in failList:
                failMessage = failObj + "\n"
            cmds.confirmDialog(title = "ERROR", message = f"The follow controls don't have an existing locator with animation: \n{failMessage} ")
                    

animWorldBakeLocators()