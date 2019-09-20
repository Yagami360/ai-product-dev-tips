# 【Python】フォルダ内のファイル一覧を取得する。

## 機械学習の文脈での用途

## 実現方法

- フォルダ内の全ファイルは、`os.listdir()` で取得出来る。
    - 但し、`os.listdir()` で取得したファイル一覧のファイル名は、ソートされていないので、`sorted()` でソートすること。
    - 機械学習のタスクにおいて list がソートされていないと，取得したファイル名一覧の for ループ中に処理が中断された時に再開ができないのでソートする必要がある。

- 特定の拡張子のファイル一覧を取得する方法には、以下のような方法がある。
    1. `os.listdir()` と文字列検索の `endswith()` を組み合わせて取得する方法。
        ```python
        image_files = [f for f in sorted(os.listdir(in_dir)) if f.endswith(('.jpg', '.png'))]
        ```
    1. `glob` モジュールを使用する方法。
        ```python
        import glob
        image_files = sorted( glob.glob(os.path.join(in_dir, '*.png')) )        
        ```