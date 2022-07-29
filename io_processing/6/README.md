# 【Python】独自の Python CLI コマンドを作成する（ローカル環境にあるファイルでインストールする場合）

## ■ 方法

1. PyPI にアカウント登録する<br>
    xxx

1. 以下の構造のプロジェクトを作成する
    ```sh
    + ${プロジェクト名（CLI名など）} 
      +--- module（任意の名前でOK）
      |    + __init__.py
      |    + main.py（任意の名前でOK）
      + setup.py   
      + requirements.txt
    ```

1. Python CLI 実行時の処理内容を定義した `main.py` のコードを作成する<br>
    作成したい Python CLI 実行時の処理内容を定義した `main.py` のコードを作成する。
    今回のケースでは簡単のため、Hello World! をコンソール画面に出力するのみのコードを作成にする

    ```python
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-
    import argparse

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('--args1', type=int, default=1 )
        parser.add_argument('--args2', type=int, default=2 )
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()
        if( args.debug ):
            for key, value in vars(args).items():
                print('%s: %s' % (str(key), str(value)))

        print("Hello World!")
        
    ```

    ポイントは、以下の通り

    - `argparse` を使用することで、`$ sample-cli --debug` といった具合に、オプション引数を指定可能な CLI コマンドになるようにしている

1. pip でインストールするための設定を定義した `setup.py` のコードを作成する<br>
    pip でインストールするための設定を定義した `setup.py` のコードを作成する
    ```python
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-
    from setuptools import setup, find_packages

    with open('requirements.txt') as requirements_file:
        install_requirements = requirements_file.read().splitlines()

    setup(
        name='sample-cli',
        version='0.0.1',
        description="sample package",
        author="yagami360",
        install_requres=install_requirements,
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                "sample-cli=module.main:main"
            ]
        }    
    )
    ```

    > `setup()` の引数 `entry_points` に設定している `"sample-cli=module.main:main"` の左辺が作成したい CIL のコマンド名になり、右辺が CLI の処理内容を定義した `main` 関数へのパスになる

1. 配布用パッケージを作成する<br>
    pip コマンドでインストールする際に使用する配布用パッケージを作成する
    ```sh
    cd sample-cli
    python setup.py sdist
    ```

    > 上記コマンドを実行することで、`dist/${CLI_NAME}-${VERSION}.tar.gz`（今回の場合は、`dist/sample-cli-0.0.1.tar.gz`）というファイルが作成される

1. パッケージをインストールする<br>
    ```sh
    ```

1. 作成した Python CLI を実行する<br>
    ```sh
    cd sample-cli
    sample-cli
    ```

## ■ 参考サイト

- https://qiita.com/kinpira/items/0a4e7c78fc5dd28bd695