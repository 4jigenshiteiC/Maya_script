# -*- coding: utf-8 -*-
#createnSimulationCmd

import maya.cmds as cmds
import maya.mel as mel

def createHairChain( Joints=[], DETAIL = 1, falloff == 1 ):
    """
    createHairChain
        nHairを使用したチェーンを作成します。

    Args:
        Joints  :   先端と末端のジョイントリスト
                    指定が無い場合は、joint選択で実行することが可能。 

        DETAIL  :   カーブのディティールを設定
                    値を上げると、自動的に生成された ikSplineHandle のカーブにあるスパンの数が増えます。 

        falloff  :   落ちぐわい
                    0　：　Quick
                    1　：　Normal
                    2　：　Gradual

    Returns:
        hairHandle  :   
        hairCurve   :   
        hsysXform   :   
    """
    if not Joints:
        joints= cmds.ls( sl = True, type="joint" )

    if len(joints) != 2:
        cmds.error( "Hair Single Chain: two joints must be selected first: root joint + joint at end of chain")

    #   Create ik Curve
    tempIKspline = cmds.ikHandle( sol="ikSplineSolver", ns=( DETAIL + 1))
    cmds.delete( tempIKspline[0],tempIKspline[1] )

    hairCurveBase = cmds.rename( tempIKspline[2], "baseCurve#" )

    #   create Hair Curve

    cmds.select( hairCurveBase, r=True)
    mel.eval( "makeCurvesDynamicHairs 0 0 0; " )

    cmds.pickWalk(d="down")
    hsys = cmds.ls( sl=True, type="hairSystem" )[0]
    #cmds.setAttr(hsys+".gravity",20)

    cmds.pickWalk(d="up")
    hsysXform = cmds.ls( sl=True )[0]

    folXform = cmds.listConnections( hsys,type="follicle" )[0]
    cmds.setAttr(folXform+".visibility",0)
    cmds.select( folXform )

    cmds.pickWalk(d="down")
    fol = cmds.ls( sl=True, type="follicle" )[0]
    cmds.setAttr(fol+".pointLock",1)

    tmp = cmds.listConnections( fol, s=False, d=True )
    hairCurve = cmds.rename( tmp[1], "hairCurve#")

    ikInfo = cmds.ikHandle( sol = "ikSplineSolver", ccv=False, snc=True, 
                            startJoint= joints[0], endEffector=joints[1], 
                            pcv=True, curve=hairCurve)

    #   Modify IK node for hair attrs
    hairHandle = cmds.rename( ikInfo[0], "hairHandle#") 

	if falloff == 0:
			cmds.setAttr( hairHandle + ".hairStiffness", .5)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_Position", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_FloatValue", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Position", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_FloatValue", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Interp", 1)
				
	elif falloff == 1:
			cmds.setAttr( hairHandle + ".hairStiffness", .5)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_Position", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_FloatValue", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Position", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_FloatValue", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Interp", 3)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_Position", .25)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_FloatValue", .25)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_Interp", 3)
		
	elif falloff == 2:
			cmds.setAttr( hairHandle + ".hairStiffness", .5)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_Position", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[1].stiffnessScale_FloatValue", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Position", 0)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_FloatValue", 1)
			cmds.setAttr( hsys[0] + ".stiffnessScale[0].stiffnessScale_Interp", 3)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_Position", .75)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_FloatValue", .75)
			cmds.setAttr( hsys[0] + ".stiffnessScale[2].stiffnessScale_Interp", 3)

    return hairHandle, hairCurve, hsysXform

def createnCloth( rootList=[], falloff = 1 ):

    """
    createnCloth
        nClothを使用したチェーンを作成します。

    Args:
        Joints  :   複数のチェーンのルートリスト
                    指定が無い場合は、joint選択で実行することが可能。 

        falloff  :   クロスの落ちぐわい
                    0　：　Quick
                    1　：　Normal
                    2　：　Gradual

    Returns:
        curveList  :   
        clothShape   :   
        clothRamp   :   
    """
    
    if not rootList:
        rootList= cmds.ls( sl = True, type="joint" )

    mode = 0 #	Create IKSpline

    #	Create curves

    curveList = []
    chainCount = 0

    for root in rootList:

        cmds.select( root, r=True )
        base = cmds.pickWalk(d="up")
        
        translateTemp = cmds.xform( root, q=True, t=True, ws=True )

        curveList.append( cmds.curve( d=True, p=translateTemp,k=False, name="dynJoint_Curve#") )

        cmds.select( root, hi=True, r=True )
        chain= cmds.ls( sl = True, type="joint" )
        
        for j in chain:
            translateTemp = cmds.xform( j, q=True, t=True, ws=True )
            cmds.curve( curveList[chainCount], a=True, p=translateTemp, os=True )
            
        #	Create IKSpline
        if mode == 0:
            cmds.ikHandle( sol="ikSplineSolver",  createCurve=0, sj=root, ee=chain[-1], c=curveList[chainCount])
            
            try:		
                cmds.parent( curveList[chainCount], base )
            except RuntimeError:
                pass
            
        chainCount += 1
        
        
    #	Create lofted mesh from curves	
    loftedMesh = cmds.loft( curveList, ch=True, u=True, c=False, ar=True, d=1, ss=1, rn=False, po=1, rsn=True, 
                    n="dynJoint_BaseMesh#" )

    nurbsTessellate = cmds.listConnections(loftedMesh[1],s=False, d=True, type="nurbsTessellate")[0]

    cmds.setAttr( nurbsTessellate + ".polygonType", 1 )
    cmds.setAttr( nurbsTessellate + ".format", 2 )
    cmds.setAttr( nurbsTessellate + ".uType", 3 )
    cmds.setAttr( nurbsTessellate + ".vType", 3 )
    cmds.setAttr( nurbsTessellate + ".uNumber", 1 )
    cmds.setAttr( nurbsTessellate + ".vNumber", 1 )

    cmds.polyNormalizeUV( loftedMesh[0], nt=1, pa=False)
    cmds.delete( loftedMesh[0], ch=True )

    aboveBase = cmds.pickWalk( base, d="up" )
    cmds.parent( loftedMesh[0], aboveBase )


    #	Create wrap deformer mesh->curves

    cmds.select( curveList, r=True )
    cmds.select( loftedMesh[0], add=True )
    mel.eval( "CreateWrap;" )

    #	Create nCloth out of lofted mesh

    cmds.currentTime( 0 )
    cmds.select( loftedMesh[0], r=True )
    mel.eval( "createNCloth 0;" )
    clothShape = cmds.rename( "dynJoint_nCloth#" )


    #	Create ramp for falloff of input mesh attract
    clothRamp = cmds.shadingNode( "ramp", asTexture=True, name = "dynJoint_nClothFalloff#" )
    placementNode = cmds.shadingNode( "place2dTexture", asUtility=True )
    cmds.connectAttr( placementNode + ".outUV" ,clothRamp + ".uv" )
    cmds.connectAttr( placementNode + ".outUvFilterSize" ,clothRamp + ".uvFilterSize" )
    cmds.setAttr( placementNode + ".wrapU",0 )

    cmds.removeMultiInstance( clothRamp + ".colorEntryList[1]", b=True )
    cmds.setAttr( clothRamp + ".colorEntryList[0].color" , 1 ,1 ,1 ,type = "double3" )
    cmds.setAttr( clothRamp + ".colorEntryList[2].color" , 0 ,0 ,0 ,type = "double3" )
    cmds.setAttr( clothRamp + ".type" ,1 )

    if falloff == 0:
        cmds.setAttr( clothRamp + ".colorEntryList[0].position", 0.05 )
        cmds.setAttr( clothRamp + ".colorEntryList[2].position", 0.30 )
    elif falloff == 1:
        cmds.setAttr( clothRamp + ".colorEntryList[0].position", 0.05 )
        cmds.setAttr( clothRamp + ".colorEntryList[2].position", 0.10 )
    elif falloff == 2:
        cmds.setAttr( clothRamp + ".colorEntryList[0].position", 0.05 )
        cmds.setAttr( clothRamp + ".colorEntryList[2].position", 0.75 )

    #   create shader for preview of falloff
    cmds.select( loftedMesh[0], r=True )
    mel.eval( "hypergraphAssignTextureToSelection {0};".format(clothRamp) )

    cmds.connectAttr( clothRamp + ".outAlpha", clothShape + ".inputAttractMap",  force=True)
    cmds.setAttr( clothShape + ".inputMeshAttract", 1)
    cmds.setAttr( clothShape + ".inputMeshAttract", l=True )


    return curveList, clothShape, clothRamp


def setCollideNCloth( MeshList = [] ):
    """
    setCollideNCloth
        メッシュをnClothのコリジョンに設定する。

    Args:
        MeshList  :   コリジョンにするメッシュリスト
                        指定が無ければ、現在選択されている。
    """
    if not MeshList:
        MeshList = cmds.ls(sl=True)

    cmds.select( MeshList, r=True)
    mel.eval( "makeCollideNCloth;" )