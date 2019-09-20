# 【Python】２つのフォルダのファイル数＆ファイル名の差分を確認する。

## 機械学習の文脈での用途

## 実現方法

- ２つのフォルダ内に存在するファイル名の比較は、`os.listdir()` で取得したファイル一覧を、集合型 `set()` にして、集合差を取ることで簡単に実現出来る。
    ```python
    $ python
    >>> import os
    >>> files_set1 = set( os.listdir("dir1") )
    >>> files_set2 = set( os.listdir("dir2") )
    >>> len( files_set1 - files_set2 )
    >>> len( files_set2 - files_set1 )
    >>> files_set1 - files_set2     # dir1 に存在して dir2 に存在しないファイル
    >>> files_set2 - files_set1     # dir2 に存在して dir1 に存在しないファイル
    ```
    - 機械学習のタスクにおいては、処理の過程で、大量の画像ファイルを別ディレクトリへコピーしたり移動したりすることが多いが、それらの処理の過程で画像ファイルが抜け落ちたり、余分なファイルが入ったりしてないか調べるときに、この手法は便利である。