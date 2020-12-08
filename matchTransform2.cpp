#include <maya/MPxCommand.h> 
#include <maya/MFnPlugin.h> 
#include <maya/MSyntax.h> 
#include <maya/MArgParser.h>  
#include <maya/MSelectionList.h>  
#include <maya/MGlobal.h> 
#include <maya/MObject.h >
#include <maya/MItSelectionList.h >
#include <maya/MFnTransform.h >
#include <maya/MTransformationMatrix.h >
#include <maya/MMatrix.h >
#include <maya/MFnDependencyNode.h >
#include <maya/MObject.h >
#include <maya/MPlug.h >
#include <maya/MFnMatrixData.h >
#include <maya/MEulerRotation.h >
#include <maya/MVector.h >
#include <maya/MQuaternion.h >
#include <maya/MDagPath.h >

class matchTransform2 : public MPxCommand
{
public:
	matchTransform2();//コンストラクター
	virtual ~matchTransform2(); //仮想関数 デストラクター
	static void* cmdCreator();
	static  MSyntax syntaxCreator();
	MStatus doIt(const MArgList& arg);
	MStatus redoIt();
	MStatus undoIt();
	bool isUndoable() const;

	static const char*  kPluginCmdName;
	static const char*  kTranslationFlag;
	static const char*  kTranslationLongFlag;
	static const char*  krotationFlag;
	static const char*  krotationLongFlag;
	static const char*  kScaleFlag;
	static const char*  kScaleLongFlag;

	static bool __translationArg;
	static bool __rotationArg;
	static bool __scaleArg;
};

static MDagPath DagPath_Source;
static MObject mObjct_Target;
static MFnTransform transformFn_Source;
static MTransformationMatrix matrix_Source;
static MObject mObjct_Source;

//	静的な変数宣言
//the name of the command
const char*  matchTransform2::kPluginCmdName = "matchTransform2";

//requests translation information
const char*  matchTransform2::kTranslationFlag = "-t";
const char*  matchTransform2::kTranslationLongFlag = "-translation";

//requests rotation information
const char*  matchTransform2::krotationFlag = "-r";
const char*  matchTransform2::krotationLongFlag = "-rotation";

//requests rotation information
const char*  matchTransform2::kScaleFlag = "-s";
const char*  matchTransform2::kScaleLongFlag = "-scale";
// std::string で宣言するとエラー

bool  matchTransform2::__translationArg = true;
bool  matchTransform2::__rotationArg = true;
bool  matchTransform2::__scaleArg = true;

//クラス定義
matchTransform2::matchTransform2()
{
}

matchTransform2::~matchTransform2()
{
}


MStatus matchTransform2::doIt(const MArgList& args)
{
	MStatus status;
	MArgParser    argData( syntaxCreator(), args, &status );


	MSelectionList slist;
	status = MGlobal::getActiveSelectionList(slist);

	if (slist.length() != 2)
	{
		displayError("This command requires exactly 2 argument to be specified or selected;");
		return status;
	}

	MItSelectionList iter(slist, MFn::kTransform);
	int count = 0;
	while (not iter.isDone())
	{
		if (count == 0)
		{

			iter.getDependNode(mObjct_Target);
		}
		else
		{
			iter.getDependNode(mObjct_Source);
			iter.getDagPath(DagPath_Source);
			transformFn_Source.setObject(DagPath_Source);
			matrix_Source = transformFn_Source.transformation();
		}

		count += 1;
		iter.next();
	}

	//	TranslationFlagを解析
	if (argData.isFlagSet(kTranslationFlag))
	{
		bool tmp;
		status = argData.getFlagArgument(kTranslationFlag, 0, tmp);
		if (!status) {
			status.perror("upside down flag parsing failed.");
			return status;
		}
		__translationArg = tmp;
	}

	//	krotationFlagを解析
	if (argData.isFlagSet(krotationFlag))
	{
		bool tmp;
		status = argData.getFlagArgument(krotationFlag, 0, tmp);
		if (!status) {
			status.perror("upside down flag parsing failed.");
			return status;
		}
		__rotationArg = tmp;
	}

	//	kScaleFlagを解析
	if (argData.isFlagSet(kScaleFlag))
	{
		bool tmp;
		status = argData.getFlagArgument(kScaleFlag, 0, tmp);
		if (!status) {
			status.perror("upside down flag parsing failed.");
			return status;
		}
		__scaleArg = tmp;
	}

	return redoIt();
}


MStatus matchTransform2::redoIt()
{
	//	Get target node matrix.
	MFnDependencyNode mFnD_Target(mObjct_Target);
	
	MObject world_matrix_attr_Target = mFnD_Target.attribute("worldMatrix");
	
	MPlug matrix_plug(mObjct_Target, world_matrix_attr_Target);
	MPlug matrix_plug_Target = matrix_plug.elementByLogicalIndex(0);

	MFnMatrixData world_FnMatrixData(matrix_plug_Target.asMObject());
	MMatrix world_matrix_data = world_FnMatrixData.matrix();


	//   Get Source node parent matrix.
	MFnDependencyNode mFnD_Source(mObjct_Source);

	MObject	parent_matrix_attr_Source = mFnD_Source.attribute("parentMatrix");

	
	MPlug parent_matrix_plug(mObjct_Source, parent_matrix_attr_Source);
	MPlug parent_matrix_plug_Source = parent_matrix_plug.elementByLogicalIndex(0);
		
	MFnMatrixData	parent_FnMatrixData(parent_matrix_plug_Source.asMObject());
	MMatrix parent_matrix_data = parent_FnMatrixData.matrix();


	//   Get order of target node.
	MPlug rotateOrderPlag = mFnD_Source.findPlug("rotateOrder", false);
	int rotateOrder_index = rotateOrderPlag.asInt();

	//   Get Transform value.
	MMatrix Matrix = world_matrix_data * parent_matrix_data.inverse();

	MTransformationMatrix mTransformationMatrix(Matrix);
	mTransformationMatrix.reorderRotation( MTransformationMatrix::RotationOrder(rotateOrder_index + 1));
	

	MVector pos = mTransformationMatrix.getTranslation(MSpace::kWorld);

	MQuaternion q = mTransformationMatrix.rotation();
	MEulerRotation rot = q.asEulerRotation();

	double scl[3];
	mTransformationMatrix.getScale(scl, MSpace::kWorld);



 
    //   Set Transform value.
	if (__translationArg) {

		MPlug translatePlag = mFnD_Source.findPlug("translate", false);
		translatePlag.child(0).setDouble(pos.x);
		translatePlag.child(1).setDouble(pos.y);
		translatePlag.child(2).setDouble(pos.z);
	}

        
	if (__rotationArg) {

		MPlug rotatePlag = mFnD_Source.findPlug("rotate", false);
		rotatePlag.child(0).setDouble(rot.x);
		rotatePlag.child(1).setDouble(rot.y);
		rotatePlag.child(2).setDouble(rot.z);
	}

 
	if (__scaleArg) {

		MPlug scalePlag = mFnD_Source.findPlug("scale", false);
		scalePlag.child(0).setDouble(scl[0]);
		scalePlag.child(1).setDouble(scl[1]);
		scalePlag.child(2).setDouble(scl[2]);
	}

	return MS::kSuccess;
}


MStatus matchTransform2::undoIt()
{

	transformFn_Source.set(matrix_Source);
	return MS::kSuccess;
}


bool matchTransform2::isUndoable() const
{
	return true;
}


void* matchTransform2::cmdCreator()
{
	return (void *)(new matchTransform2);
}

MSyntax matchTransform2::syntaxCreator()
{

	//Specify custom syntax
	MSyntax syntax;
	syntax.addFlag(matchTransform2::kTranslationFlag, matchTransform2::kTranslationLongFlag, MSyntax::kBoolean);
	syntax.addFlag(matchTransform2::krotationFlag, matchTransform2::krotationLongFlag, MSyntax::kBoolean);
	syntax.addFlag(matchTransform2::kScaleFlag, matchTransform2::kScaleLongFlag, MSyntax::kBoolean);
	syntax.useSelectionAsDefault(true); // if a selection list argument is not specified when the command is entered, then use the current selection
	syntax.setObjectType(MSyntax::kSelectionList, 2, 2);// this specifies we want the objects as an MSelectionList that may contain only 1 item
	return syntax;
}


// プラグインの登録部分
MStatus initializePlugin(MObject obj)
{
	MStatus   status;//メソッドが失敗したかどうかを判断できる
	MFnPlugin plugin(obj, "Shigehiro", "1.0", "Any");
	status = plugin.registerCommand(
		matchTransform2::kPluginCmdName,
		matchTransform2::cmdCreator,
		matchTransform2::syntaxCreator
	);
	return status;
}


// プラグインの解除部分
MStatus uninitializePlugin(MObject obj)
{
	MStatus   status;
	MFnPlugin plugin(obj);
	status = plugin.deregisterCommand(matchTransform2::kPluginCmdName);
	return status;
}
