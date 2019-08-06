## 【シェルスクリプト】フォルダ内のファイル数を確認する。

- フォルダ内のファイル数は、`$ ls -1 | wc -l` で確認出来る。
    - `$ ls -1 | wc -l` では、サブディレクトリ内の全ファイル数を表示することに注意。
    ```sh
    #!bin/bash
    DIR="dir"  # 相対パスで指定

    echo ${DIR}
    ls ${DIR} | wc -l

    echo ${DIR}/sub_dir1
    ls ${DIR}/sub_dir1 | wc -l

    echo ${DIR}/sub_dir2
    ls ${DIR}/sub_dir2 | wc -l
    ```

- 複数フォルダのファイル数確認は、以下のシェルコマンドで実行可能
    ```sh
    $ ls | while read name

    > do
    > echo $name
    > done

    $ ls | while read name; do echo $name; ls -1 $name | wc -l; done
    ```