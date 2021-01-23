# -*- coding: utf-8 -*-
#createnSimulationCmd
import maya.cmds as cmds
import glob

def main():
	dMaterialName = {
	"body_01" : ["body", ],
	"cheek_00" : ["mat_cheek", ],
	"eye_iris_L_00" : ["eye_L1", ],
	"eye_iris_R_00" : ["eye_R1", ],
	"eyeline_00" : [ "eyebase", "eyeline" ],
	"face_00" : ["face", ],
	"hair_01" : ["hair", ],
	"skin_01" : ["skin1", ],
	}

	FBX = cmds.fileDialog( m=False,dm='*.fbx' )
	
	
	if FBX:
		cmds.file( fbx, i=True, type="FBX")
		
		textureFolder = "\\".join( fbx.split("\\")[:-1] )
		
		dTextures = {}
		for tga in glob.glob(textureFolder + "\\*\\Texture\\*.tga"):
			tagaName = tga.split("\\")[-1].split(".")[0]	
			
			if  not tagaName in dMaterialName.keys():
				continue
			for matName in dMaterialName[tagaName]:
				dTextures.update( { matName : tga } )
		
		mats = cmds.ls( mat=True,type="cgfxShader"  )
		
		for mat in set(mats):
			if not mat in dTextures.keys():
				continue
			
			connectionsList = cmds.listConnections( mat+ ".outColor", d=True, s=False, p=True )
			tex = dTextures[mat]
				
			lambert = cmds.shadingNode( "lambert", asShader=True, name = "lambert_" + mat)
			
			file = cmds.shadingNode( "file", asTexture=True, isColorManaged=True )
			place2dTexture = cmds.shadingNode( "place2dTexture", asUtility=True )
			
			attrList = [ "coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger", 
						 "wrapU", "wrapV", "repeatUV", "offset", "rotateUV", "noiseUV", "vertexUvOne",
						 "vertexUvTwo", "vertexUvThree", "vertexCameraOne" ] 
			
			for attr in attrList:
				cmds.connectAttr( "{0}.{1}".format( place2dTexture,attr ), "{0}.{1}".format( file,attr ), f=True )
			cmds.connectAttr( "{0}.outUV".format( place2dTexture ), "{0}.uv".format( file ), f=True )
			cmds.connectAttr( "{0}.outUvFilterSize".format( place2dTexture ), "{0}.uvFilterSize".format( file ), f=True )
			cmds.connectAttr( "{0}.outColor".format( file ), "{0}.color".format( lambert ), f=True )
			cmds.connectAttr( "{0}.outColor".format( file ), "{0}.ambientColor".format( lambert ), f=True )
			
			cmds.setAttr( "{0}.fileTextureName".format(file) , tex, type="string" )
			
			
			for connect in connectionsList:
				try:
					cmds.disconnectAttr( mat + ".outColor", connect )
					cmds.connectAttr( lambert + ".outColor", connect )
				except:
					pass
		
if __name__ == "__main__":
	main()			