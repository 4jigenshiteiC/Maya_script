import maya.api.OpenMaya as om

class matchTransform2(om.MPxCommand):
    """PYTHON
    A command that prints a string to the console.
    """
    
    #   the name of the command
    kPluginCmdName = "matchTransform2"
 
    # requests translation information   
    kTranslationFlag = '-t'
    kTranslationLongFlag = '-translation'
 
    # requests rotation information
    krotationFlag = '-r'
    krotationLongFlag = '-rotation'
 
    # requests Scale information
    kScaleFlag = '-s'
    kScaleLongFlag = '-scale'
    
 
    def __init__(self):
        """
        Initialize the instance.
        """
        om.MPxCommand.__init__(self)
 
        self.__translationArg = True
        self.__rotationArg = True
        self.__scaleArg = True
 
    def doIt(self, args):
        """
        Parse arguments and then call doItQuery()
        """
        # parse the arguments
        try: argData = om.MArgDatabase(self.syntax(), args)
        except: pass
        else:
            try:
                sList = argData.getObjectList()
                if sList.length() != 2:
                    raise Exception(
                        'This command requires exactly 2 argument to be specified or selected;')
 
                iter = om.MItSelectionList(sList, om.MFn.kTransform)
 
                count = 0
                while not iter.isDone():  
                    if count == 0:
                        self.mObjct_Target = iter.getDependNode()
                    else:
                        self.mObjct_Source = iter.getDependNode()
                        self.DagPath_Source = iter.getDagPath()
                        
                        self.transformFn_Source = om.MFnTransform()
                        self.transformFn_Source.setObject(self.DagPath_Source)
                        self.matrix_Source = self.transformFn_Source.transformation()
 
                    count += 1
                    iter.next()
 
                if argData.isFlagSet(matchTransform2.kTranslationFlag):
                    self.__translationArg = argData.flagArgumentInt(matchTransform2.kTranslationFlag, 0)
                if argData.isFlagSet(matchTransform2.krotationFlag):
                    self.__rotationArg = argData.flagArgumentInt(matchTransform2.krotationFlag, 0)
                if argData.isFlagSet(matchTransform2.kScaleFlag):
                    self.__scaleArg = argData.flagArgumentInt(matchTransform2.kScaleFlag, 0)
 
                self.redoIt()
            except: pass
 
    def redoIt(self):
        self.doItQuery()
 
    def undoIt(self):
        self.transformFn_Source.setTransformation(self.matrix_Source)
 
    def isUndoable(self):
        """
        Determine undoability based on command mode.
        """
        return True
 
    def doItQuery(self):
        #   Get target node matrix.
        mFnD_Target = om.MFnDependencyNode(self.mObjct_Target)
        world_matrix_attr_Target = mFnD_Target.attribute("worldMatrix")
        matrix_plug_Target = om.MPlug(self.mObjct_Target, world_matrix_attr_Target).elementByLogicalIndex(0)
        world_matrix_data = om.MFnMatrixData( matrix_plug_Target.asMObject()).matrix()
        
 
        #   Get Source node parent matrix.
        mFnD_Source = om.MFnDependencyNode(self.mObjct_Source)
        parent_matrix_attr_Source = mFnD_Source.attribute("parentMatrix")
        parent_matrix_plug_Source = om.MPlug(self.mObjct_Source, parent_matrix_attr_Source).elementByLogicalIndex(0)
        parent_matrix_data = om.MFnMatrixData( parent_matrix_plug_Source.asMObject()).matrix()
 
        #   Get order of target node.
        rotateOrderPlag = mFnD_Source.findPlug("rotateOrder",False)
        rotateOrder = rotateOrderPlag.asInt()
        
 
        #   Get Transform value.
        Matrix = world_matrix_data * parent_matrix_data.inverse()
 
        mTransformationMatrix = om.MTransformationMatrix(Matrix)
        mTransformationMatrix.reorderRotation( rotateOrder + 1 )
        pos = mTransformationMatrix.translation(om.MSpace.kWorld)
        scl = mTransformationMatrix.scale(om.MSpace.kWorld)
        rot = mTransformationMatrix.rotation(False)
 
        #   Set Transform value.
        if self.__translationArg:
            translatePlag = mFnD_Source.findPlug("translate",False)
            translatePlag.child(0).setDouble(pos.x)
            translatePlag.child(1).setDouble(pos.y)
            translatePlag.child(2).setDouble(pos.z)
        
        if self.__rotationArg:
            rotatePlag = mFnD_Source.findPlug("rotate",False)
            rotatePlag.child(0).setDouble(rot.x)
            rotatePlag.child(1).setDouble(rot.y)
            rotatePlag.child(2).setDouble(rot.z)
 
        if self.__scaleArg:  
            scalePlag = mFnD_Source.findPlug("scale",False)
            scalePlag.child(0).setDouble(scl[0])
            scalePlag.child(1).setDouble(scl[1])
            scalePlag.child(2).setDouble(scl[2])
 
 
    @classmethod
    def cmdCreator(cls):
        """
        Return pointer to proxy object.
        """
        return cls()
 
    @classmethod
    def syntaxCreator(cls):
        """
        Specify custom syntax
        """
        syntax = om.MSyntax()
        syntax.addFlag(cls.kTranslationFlag, cls.kTranslationLongFlag, om.MSyntax.kBoolean)
        syntax.addFlag(cls.krotationFlag, cls.krotationLongFlag, om.MSyntax.kBoolean)
        syntax.addFlag(cls.kScaleFlag, cls.kScaleLongFlag, om.MSyntax.kBoolean)
        syntax.useSelectionAsDefault(True) # if a selection list argument is not specified when the command is entered, then use the current selection
        syntax.setObjectType(om.MSyntax.kSelectionList, 2, 2) # this specifies we want the objects as an MSelectionList that may contain only 1 item
        return syntax
 
 
def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass
 
def initializePlugin(obj):
    """
    Initialize the plug-in.
    """
    plugin = om.MFnPlugin(
        obj,
        'Shigehiro Ochi',
        '1.0',
        'Any'
    )
    try:
        plugin.registerCommand(
            matchTransform2.kPluginCmdName,
            matchTransform2.cmdCreator,
            matchTransform2.syntaxCreator
        )
    except:
        raise Exception(
            'Failed to register command: %s'%
            matchTransform2.kPluginCmdName
        )
 
def uninitializePlugin(obj):
    """
    Uninitialize the plug-in
    """
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterCommand(matchTransform2.kPluginCmdName)        
    except:
        raise Exception(
            'Failed to unregister command: %s'%
            matchTransform2.kPluginCmdName
        )

