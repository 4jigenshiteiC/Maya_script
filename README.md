# Maya_script
Created Maya script storage




## soAddNoiseToAnimationCurve.py

**概要**

アニメーションカーブ（Fカーブ）にノイズを追加します。

**使用方法**


- スクリプトエディタのファイルを読み込み実行

- C:\Users\<ユーザー名>\Documents\maya\scripts にファイル保存。<br>下記のコードを実行する。<br>
```
import soAddNoiseToAnimationCurve
soAddNoiseToAnimationCurve.addNoiseWindow.showUI()
```

**GUI**

![demo](https://github.com/4jigenshiteiC/Maya_script/blob/item/gui.PNG)

Select Layer　： ノイズを追加するレイヤ設定

- BaseAnimation　：　ペース

- New AnimaLayer　：　新しいアニメーションレイヤを作成する

- Select AnimLayer　：　現在あるアニメーションレイヤを選択する


Frame Range　：　ノイズを追加する範囲とステップフレームの設定

Transform　：　ノイズを追加するトランスフォームを設定

Noise setting　：　ノイズの最大値と最小値の設定

- Adsolute value　：　設定した値を絶対数として扱う　

- Reative value　：　設定した値を相対的に加算する

Impact　：　ノイズの影響度の設定



**デモ**

![demo](https://github.com/4jigenshiteiC/Maya_script/blob/item/addNoiseToAnimationCurve.gif)

**バージョン**

1.00　リリース

**備考**

- 1点確認済みのバグがあります。<br>アニメーションレイヤを削除し、【Select Layer ＞ Select AnimaLayer】に設定するとメニューが空になります。<br>ウィンドウを開きなおしてください。



## soViewSwitching

**概要**

MotionBuilderっぽいビュー切り替え
Maya Advent Calendar 2019の1日目（ https://qiita.com/amanatsu-knit/items/199c412f00b646b0ae61 ）を参考に制作。

**使用方法**

ファイルを、Documents/maya/scripts に置いてください。
ホットキー設定で下記のコードを設定してください。

```
import soViewSwitching
soViewSwitching.ViewSwitching("front") 
```

"front"の部分は、必要に応じて、"persp" or "top" or "side" に書き換えてください。
