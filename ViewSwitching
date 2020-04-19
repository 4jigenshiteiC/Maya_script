import maya.cmds as cmds

def ViewSwitching(View):
	"""
	View switching like MotionBuilder.
	(MotionBuilderっぽいビュー切り替え)
	
	Args:
		View(String): Camera view.("persp" or "top" or "front" or "side")
	"""
	
	Panele = cmds.getPanel( withFocus=True )
	
	if Panele[:10] == "modelPanel":	
		cam = cmds.modelPanel(Panele, q=True,cam=True)
	
		#	Switch to specified view　指定ビューに切り替え
		if cam != View:
			cmds.modelPanel(Panele, e=True,cam=View)
			
		#	Reverse view　ビューの反転
		else:
			pos = cmds.xform( cam, q=True, t=True, ws=True )
			rot = cmds.xform( cam, q=True, ro=True, ws=True )
			if cam == "front":
				cmds.setAttr( "{0}.tz".format(cam), pos[2] * -1)
				if rot[1] == 0:
					cmds.setAttr( "{0}.ry".format(cam), 180 )
				elif rot[1] == 180:
					cmds.setAttr( "{0}.ry".format(cam), 0 )	
			elif cam == "side":
				cmds.setAttr( "{0}.tx".format(cam), pos[0] * -1)
				cmds.setAttr( "{0}.ry".format(cam), rot[2] * -1)			
			elif cam == "top":
				cmds.setAttr( "{0}.ty".format(cam), pos[1] * -1)
				cmds.setAttr( "{0}.rx".format(cam), rot[0] * -1)
