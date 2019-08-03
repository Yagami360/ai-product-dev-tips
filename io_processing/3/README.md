
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