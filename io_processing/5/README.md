# 【Python】独自の Python CLI コマンドを作成する

## ■ 方法

1. 以下の構造のプロジェクトを作成する
    ```sh
    + ${プロジェクト名（CLI名など）} 
      +--- module
      |    + __init__.py
      |    + main.py
      + setup.py   
      + requirements.txt
    ```

1. Python CLI 実行時の処理内容を定義した `main.py` のコードを作成する<br>
    作成したい Python CLI 実行時の処理内容を定義した `main.py` のコードを作成する。
    今回のケースでは簡単のため、Hello World! をコンソール画面に出力するのみのコードを作成にする

    ```python
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    def main():
        print("Hello World!")
    ```

1. pip でインストールするための設定を定義した `setup.py` のコードを作成する<br>
    pip でインストールするための設定を定義した `setup.py` のコードを作成する
    ```python
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    from setuptools import setup, find_packages

    with open('requirements.txt') as requirements_file:
        install_requirements = requirements_file.read().splitlines()

    setup(
        name='samplecli',
        version='0.0.1',
        description="sample package",
        author="yagami360",
        install_requres=install_requirements,
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                "command_name=module.main:main"
            ]
        }    
    )
    ```

1. Python CLI をインストールする
    1. ローカル環境にあるファイルで pip でインストールする場合<br>
        ```sh
        cd samplecli
        python3 -m pip install -e .
        ```

    1. PyPI にパッケージを公開して pip でインストールする場合<br>
        ```sh
        ```

1. 作成した Python CLI を実行する<br>
    1. ローカル環境にあるファイルで pip でインストールした場合<br>
        ```sh
        cd samplecli
        sample-cli
        ```

## ■ 参考サイト

- https://zenn.dev/d_forest/articles/b8358c56725e51da43d9
- xxx