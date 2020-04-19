# Maya_script
Created Maya script storage

## ViewSwitching

**概要**

MotionBuilderっぽいビュー切り替え
Maya Advent Calendar 2019の1日目（ https://qiita.com/amanatsu-knit/items/199c412f00b646b0ae61 ）を参考に制作。

**使用方法**

ファイルを、Documents/maya/scripts に置いてください。
ホットキー設定で下記のコードを設定してください。

```
import ViewSwitching
ViewSwitching.ViewSwitching("front") 
```

"front"の部分は、必要に応じて、"persp" or "top" or "side" に書き換えてください。
