# -*- coding: utf-8 -*-
#	------------------------------------------------------
#	soAddNoiseToAnimationCurve
#		Fカーブにノイズを追加するツール
#	------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

import random
import sys

def createRampAttrbute( nodeName, rampName ):
	"""
	createRampAttrbute
		RampAttrbuteを設定します。
		https://gist.github.com/ryusas/699ad3f5fa8469a00e8df4b3672aa89f
	Args:
		String　nodeName  :   RampAttrbuteの追加するノード名
		String　rampName  :   RampAttrbute名
	"""
	cmds.addAttr( nodeName, ln=rampName, at='compound', nc=3, m=True)
	cmds.addAttr( nodeName, ln='ramp_Position', at='float', p=rampName, dv=-1)
	cmds.addAttr( nodeName, ln='ramp_FloatValue', at='float', p=rampName, dv=-1)
	cmds.addAttr( nodeName, ln='ramp_Interp', at='enum', en='None:Linear:Smooth:Spline', dv=1, min=0, max=3, p=rampName)
	cmds.setAttr( '{0}.{1}[0]'.format(nodeName, rampName), 0, 1, 2)
	cmds.setAttr( '{0}.{1}[1]'.format(nodeName, rampName), 1, 1, 2)

def getValueRampAttrbute( nodeName, rampName, position ):
	"""
	getValueRampAttrbute
		RampAttrbuteの値を取得します。
	Args:
		String　nodeName  :   RampAttrbuteの追加されているノード名
		String　rampName  :   RampAttrbute名
		Float　position  :   position値（0～1）
	Returns:
		Float	value  :   Rampの値
	"""
	sel = om.MSelectionList().add(nodeName)
	dnFn = om.MFnDependencyNode( sel.getDependNode(0) )
	rampPlug = dnFn.findPlug(rampName, False)
	rampAttrbute = om.MRampAttribute( rampPlug )
	value = rampAttrbute.getValueAtPosition( position )
	
	return value

def rampLayout( nodeName, rampName ):
	"""
	rampLayout
		rampをレイアウトします。
	Args:
		String　nodeName  :   RampAttrbuteの追加されているノード名
		String　rampName  :   RampAttrbute名
	"""
	mel.eval('if (! exists("AEmakeLargeRamp")) source AEaddRampControl')
	mel.eval('AEmakeLargeRamp("{0}.{1}", 0, 0, 0, 0, 0)'.format(nodeName, rampName))


def fit(parameter, startValue1, endValue1, startValue2=0, endValue2=1):
	"""
	fit
		値の範囲を別の値にマッピングする。
	Args:
		Float　parameter  :   パラメータ
		Float　startValue1  :   開始値1
		Float　endValue1  :   終了値1
		Float　startValue2 :   開始値2
		Float　endValue2  :   終了値2
	Returns:
		Float	value  :   マッピングされたの値
	"""	
	if parameter < startValue1:
		parameter = startValue1
	if parameter > endValue1:
		parameter = endValue1
	
	Span1 = endValue1 - startValue1
	Span2 = endValue2 - startValue2

	rate = float( parameter - startValue1 ) / Span1
	value = startValue2 + ( rate * Span2 )

	return value

def getAnimLayerList():
	"""
	getAnimLayerList
		シーン内のアニメーションレイヤをリスト化する。
	Returns:
		List	animLayers  :   アニメーションレイヤのリスト
	"""	
	animLayers = cmds.ls(type="animLayer")

	if animLayers:
		animLayers.remove("BaseAnimation")
		
	return animLayers

def selectAnimLayer( LayerName ):
	"""
	selectAnimLayer
		指定したアニメーションレイヤを選択する。
	Args:
		String　LayerName  :   アニメーションレイヤ名
	Returns:
		String	LayerName  :   アニメーションレイヤ名
	"""		
	#	アニメーションレイヤが無い場合
	if not cmds.animLayer( q=True, r=True) and LayerName == "BaseAnimation":
		return "BaseAnimation"
		
	#	レイヤ作成
	if not cmds.animLayer( LayerName, q=True, ex=True ):
		LayerName = cmds.animLayer( LayerName,aso=True )
	
	#	レイヤを選択
	for animLayer in cmds.ls(type="animLayer"):
		mel.eval("animLayerEditorOnSelect {0} 0;".format(animLayer))
	mel.eval("animLayerEditorOnSelect {0} 1;".format(LayerName))

	return LayerName






def addNoiseToAnimationCurves( obj, LayerName="BaseAnimation", StartFrame=0, EndFrame=100, StepFrame=1, 
									TransformList=["tx","ty","tz"], nodeName=None, rampName=None,
									Absolute=False, minValue=0, maxValue=0 ):
	"""
	addNoiseToAnimationCurves
		アニメーションカーブにノイズを追加する。
	Args:
		String	obj  :   オブジェクト名
		
		String	LayerName  :   アニメーションレイヤ名
		int　StartFrame  :   開始フレーム
		int　EndFrame  :   終了フレーム
		int　StepFrame :   ステップフレーム
		list　TransformList  :   ノイズを咥えるTransformListリスト
		
		String	nodeName  :   
		
		String	rampName  :   
		
		Boolean Absolute  :   絶対値or相対値
		
		Float minValue  :   ノイズの最小値
		
		Float maxValue  :   ノイズの最大値	
	"""	
	
	#	Select Layer
	LayerName = selectAnimLayer( LayerName )

	#	Add keys
	TotalFrame = []
	for i in range( StartFrame, EndFrame+1, StepFrame ):
		TotalFrame.append(i)
	
	#	レイヤにオブジェクトを追加
	if not LayerName == "BaseAnimation":
		cmds.animLayer( LayerName, e=True,aso=True,evs=True )
	
	#	設定に基づいてキーを打つ
	for Transform in TransformList:
		if cmds.keyframe( obj, q=True, at=Transform,kc=True) == 0:
			
			initialValue = cmds.getAttr("{0}.{1}".format( obj, Transform ))
			
			if LayerName == "BaseAnimation":
				cmds.setKeyframe( obj, t=TotalFrame, at=Transform,v=initialValue,nr=True )
			else:
				cmds.setKeyframe( obj, t=TotalFrame, at=Transform,v=0,al=LayerName,nr=True )
		else:	
			if LayerName == "BaseAnimation":
				cmds.setKeyframe( obj, t=TotalFrame, at=Transform,i=True )
			else:
				cmds.setKeyframe( obj, t=TotalFrame, at=Transform,i=True,al=LayerName )
		
	
	#	ランダム的にキーをずらす
	for Frame in TotalFrame:
		if nodeName:
			#	フレーム範囲を0~1範囲に転写する。
			fitValue = fit( Frame, StartFrame, EndFrame, 0, 1)
			#	ランプから値を取得する
			rampValue = getValueRampAttrbute( nodeName, rampName, fitValue )
		for Transform in TransformList:
			#	ノイズ値
			noiseValue = random.uniform( float(maxValue), float(minValue) ) * rampValue
			value =  cmds.getAttr("{0}.{1}".format( obj, Transform ), t=Frame)

			if Absolute:
				cmds.setKeyframe( obj, t=(Frame,Frame), at=Transform,v= noiseValue )
			else:
				cmds.setKeyframe( obj, t=(Frame,Frame), at=Transform,v=( value + noiseValue) )
		
	
class addNoiseWindow(object):
	@classmethod
	def showUI(cls):
		"""
		showUI
			UIを表示させます。
		"""	
		win = cls()
		win.create()
		return win
		
	def deleteUI(self, *args):
		"""
		deleteUI
			UIを削除します。
			rampアトリビュート用のNullを削除します。
		"""	
		cmds.deleteUI(self.window, window=True)
		self.deleteRampNode()
	
	def deleteRampNode(self, *args):
		"""
		deleteRampNode
			rampアトリビュート用のNullを削除します。
			ウィンドウの×を押した時のコマンド用。
		"""	
		if cmds.ls(self.nodeName):
			cmds.delete( self.nodeName )
	
	def __init__(self):
		"""
		__init__
			初期化。
		"""	
		
		oSet = cmds.ls(sl=True)
		
		if oSet:
			self.oObj = oSet[0]
		else:
			self.oObj = None
		
		self.window = 'addNoiseWindow'
		self.title = 'Adding noise to animation curves'
		self.width=400
		
		self.addLayerName="addNoiseLayer#"
		
		self.StartFrame = cmds.playbackOptions( q=True, min=True )
		self.EndFrame = cmds.playbackOptions( q=True, max=True )
		self.StepFrame = 1
		
		self.TransformList = []

		self.rampName = "ramp"
		self.nodeName = "rampNull"

		self.Absolute = False 
		self.minValue = 0.
		self.maxValue = 0.
		
	def bt_addNoise(self, *args):
		"""
		bt_addNoise
			ボタン実行コマンド。
		"""	
		
		self.oSet = cmds.ls(sl=True)
		
		if self.oSet:
			self.oObj = cmds.ls(sl=True)[0]
		else:
			cmds.error( u"ノイズを追加するノードを選択してください。" )
			sys.exit()
		
		#	Select Layer Mode
		if cmds.radioButtonGrp( self.SelectLayer1, q=True, sl=True ):
			self.LayerName="BaseAnimation"
		if cmds.radioButtonGrp( self.SelectLayer2, q=True, sl=True ):
			self.LayerName = self.addLayerName
		if cmds.radioButtonGrp( self.SelectLayer3, q=True, sl=True ):
			self.LayerName = cmds.optionMenu( self.SteamelectAnimLayer, q=True, v=True )
			if not self.LayerName:
				self.LayerName="BaseAnimation"	
			
		#	FrameRange
		self.StartFrame = cmds.intField( self.StartFrame_if, q=True,v=True )
		self.EndFrame = cmds.intField( self.EndFrame_if, q=True,v=True )
		self.StepFrame = cmds.intField( self.StepFrame_if, q=True,v=True )		
			
		#	transform List
		self.TransformList = []
		if cmds.checkBoxGrp( self.translate, q=True, v1=True ):
			self.TransformList.append("tx")
		if cmds.checkBoxGrp( self.translate, q=True, v2=True ):
			self.TransformList.append("ty")
		if cmds.checkBoxGrp( self.translate, q=True, v3=True ):
			self.TransformList.append("tz")

		if cmds.checkBoxGrp( self.rotate, q=True, v1=True ):
			self.TransformList.append("rx")
		if cmds.checkBoxGrp( self.rotate, q=True, v2=True ):
			self.TransformList.append("ry")
		if cmds.checkBoxGrp( self.rotate, q=True, v3=True ):
			self.TransformList.append("rz")
		
		if cmds.checkBoxGrp( self.scale, q=True, v1=True ):
			self.TransformList.append("sx")
		if cmds.checkBoxGrp( self.scale, q=True, v2=True ):
			self.TransformList.append("sy")
		if cmds.checkBoxGrp( self.scale, q=True, v3=True ):
			self.TransformList.append("sz")
			
			
		#	noise setting
		if cmds.radioButtonGrp( self.Absolute_RB, q=True, sl=True ) == 1:
			self.Absolute = True
		else:
			self.Absolute = False
		
		self.minValue = cmds.floatField( self.minValue_ff, q=True, v=True )
		self.maxValue = cmds.floatField( self.maxValue_ff, q=True, v=True )

		#	処理を一旦止めて、ノイズを追加
		cmds.ogs(p=True)
		addNoiseToAnimationCurves(	self.oObj, self.LayerName, self.StartFrame, self.EndFrame, self.StepFrame, 
									self.TransformList, self.nodeName, self.rampName,
									self.Absolute, self.minValue, self.maxValue )
		cmds.ogs(p=True)

	def rb_MenuEnable(self, *args):
		"""
		rb_MenuShowOrHide
			メニューの有効、無効
		"""	
		if cmds.radioButtonGrp( self.SelectLayer1, q=True, sl=True ):
			cmds.optionMenu(self.SteamelectAnimLayer, e=True, en=False)
		if cmds.radioButtonGrp( self.SelectLayer2, q=True, sl=True ):
			cmds.optionMenu(self.SteamelectAnimLayer, e=True, en=False)
		if cmds.radioButtonGrp( self.SelectLayer3, q=True, sl=True ):
			cmds.optionMenu(self.SteamelectAnimLayer, e=True, en=True, dai=True)	
			for AnimLayer in getAnimLayerList():
				cmds.menuItem( l=AnimLayer )
		
	def create(self):
		"""
		create
			レイアウト作成。
		"""	
		
		#	多重ウィンドウ対応
		if cmds.window(self.window, exists=True):
			self.deleteUI()

		#	rampアトリビュート用Nullを作成
		cmds.group(em=True, n=self.nodeName)
		createRampAttrbute( self.nodeName, self.rampName )
		cmds.select( self.oObj, r=True )

		#	ウィンドウ作成
		self.window = cmds.window( self.window, t=self.title, w=self.width, cc=self.deleteRampNode )

		cmds.columnLayout()

		#	Layout　Select Layer
		cmds.frameLayout( l="Select Layer", w=self.width, bgc=[0.6,0,0] )
		cmds.rowColumnLayout( nc=2, cw=[[1, self.width /2], [2, self.width /2]])
		self.SelectLayer1 = cmds.radioButtonGrp( nrb=1, label="BaseAnimation ", sl=1, w=self.width, cc=self.rb_MenuEnable )
		cmds.text(" ")
		self.SelectLayer2 = cmds.radioButtonGrp( nrb=1, scl=self.SelectLayer1, label="New AnimLayer ", cc=self.rb_MenuEnable )
		cmds.text(" ")
		self.SelectLayer3 = cmds.radioButtonGrp( nrb=1, scl=self.SelectLayer1, label="Steamelect AnimLayer ", cc=self.rb_MenuEnable )
		self.SteamelectAnimLayer = cmds.optionMenu(en=False)
		for AnimLayer in getAnimLayerList():
			self.AnimLayerList = cmds.menuItem( l=AnimLayer )

			
		cmds.setParent(u=True)
		cmds.setParent(u=True)
		
		#	Layout　Frame Range
		cmds.frameLayout( l="Frame Range", w=self.width, bgc=[0.6,0,0] )
		
		cmds.rowColumnLayout(  nc=3, cw=[[1, self.width /3], [2, self.width /3], [3, self.width /3]])
		self.StartFrame_if = cmds.intField(v=self.StartFrame)
		cmds.text("~")
		self.EndFrame_if = cmds.intField(v=self.EndFrame)
		cmds.setParent(u=True)
		
		cmds.rowColumnLayout(  nc=2, cw=[[1, self.width /2], [2, self.width/2]])
		cmds.text("Step Frame  :")
		self.StepFrame_if = cmds.intField(v=self.StepFrame,min=1)
		cmds.setParent(u=True)
		
		#	Layout　transform
		cmds.frameLayout( l="transform", w=self.width, bgc=[0.6,0,0] )
		cmds.rowColumnLayout(  nc=1 )
		self.translate = cmds.checkBoxGrp( ncb=3, l='translate : ', la3=['x', 'y', 'z'], va3=[True,True,True] )
		self.rotate = cmds.checkBoxGrp( ncb=3, l='rotate : ', la3=['x', 'y', 'z'], va3=[False,False,False] )
		self.scale = cmds.checkBoxGrp( ncb=3, l='scale : ', la3=['x', 'y', 'z'], va3=[False,False,False] )
		cmds.setParent(u=True)
		
		#	Layout　noise setting
		cmds.columnLayout()
		cmds.frameLayout( l="noise setting", w=self.width, cll=False, cl=False, bgc=[0.6,0,0])
		self.Absolute_RB = cmds.radioButtonGrp( nrb=2, la2=[u"Absolute value",u"Relative value"], sl=2, w=self.width )
		
		cmds.rowColumnLayout(  nc=4, cw=[[1, self.width /4], [2, self.width /4], [3, self.width /4], [4, self.width /4]])
		cmds.text("minValue")
		self.minValue_ff = cmds.floatField(v=self.minValue)
		cmds.text("maxValue")
		self.maxValue_ff = cmds.floatField(v=self.maxValue)
		cmds.setParent(u=True)
		
		#	Layout　Impact
		cmds.frameLayout( l="Impact", w=self.width, bgc=[0.6,0,0])
		cmds.separator( h=2, st="none", w=self.width )
		rampLayout( self.nodeName, self.rampName )
		cmds.setParent(u=True)
		cmds.setParent(u=True)
		cmds.separator( h=6, st="in", w=self.width )
		
		#	Layout　button
		cmds.rowColumnLayout(  nc=3, cw=[[1, self.width /3], [2, self.width /3], [3, self.width /3]])
		cmds.button( l="Add" )
		cmds.button( l="Apply", c = self.bt_addNoise )
		cmds.button( l="Close" , c= self.deleteUI )
		cmds.setParent(u=True)
				
		cmds.showWindow(  )
		

if __name__ == '__main__':

	addNoiseWindow.showUI()