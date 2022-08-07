# gitflow-exercises

git-flow とは Git における以下のようなリポジトリのブランチルールであり、そのルールにそって git を操作する CLI コマンドである。

<img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/183292248-99121feb-640a-4469-b509-35b3f9bb7458.png">

- `master` ブランチ<br>
    ユーザにプロダクトとしてリリースするソースコードを管理するブランチで、`master/0.1`, `master/0.2` のようにタグでバージョン管理する

- `develop` ブランチ<br>
    開発作業を行うブランチ。

- `feature/xxx` ブランチ<br>
    機能の追加用ブランチで、`develop` ブランチから git checkout して作成する。開発が終わったら `develop` ブランチにマージする

- `release` ブランチ<br>
    リリース直前にバグ修正などの微調整を行うためのブランチ。`develop` ブランチから git checkout して作成する。開発が終わったら `master` ブランチと `develop` ブランチにマージする

- `hotfixes` ブランチ<br>
    リリースされたバージョンで発生したバグを速やかに修正するためのブランチ。`master` ブランチから分岐し、 `master` にマージし、タグをつける。次に `develop` にマージする。

## ■ 対象レポジトリ

- https://github.com/Yagami360/gitflow-exercises

## ■ 方法

1. git flow をインストールする<br>
    - Mac OS の場合<br>
        ```sh
        brew install git-flow
        ```

    - Linux の場合<br>
        ```sh
        ```

1. git flow を初期化する<br>
    ```sh
    git flow init -d
    ```
    - `-d` : ブランチ名を自動で作成

    上記コマンドを実行することで、`master` ブランチと `develop` ブランチが作成され、`develop` に checkout される

    ```sh
    $ git branch
    * develop
      master
    ```

1. `git flow` を使用して `feature` ブランチを操作する<br>
    - `feature` ブランチを作成する場合<br>
        `develop` から新しい機能を追加する場合は、以下のコマンドを実行する<br>

        ```sh
        git flow feature start ${BRANCH_NAME}
        ```

        このコマンドを実行することで `feature/xxx` ブランチが作成される
        ```sh
        $ git branch
          develop
        * feature/feature1
          master
        ```

    - 新たに作成した `feature/xxx` ブランチを `develop` ブランチに merge する場合
        ```sh
        git add .
        git commit -m "a"
        git flow feature finish ${BRANCH_NAME}
        ```

        このコマンドを実行することで、`feature/xxx` ブランチが `develop` ブランチに merge され、`feature/xxx` ブランチが削除される
        ```sh
        $ git branch
        * develop
          master
        ```

    - 新たに作成した `feature/xxx` ブランチを `develop` ブランチに merge し、GitHub レポジトリに push する場合
        ```sh
        git add .
        git commit -m "a"
        git flow feature publish ${BRANCH_NAME}
        ```

        ```sh
        $ git branch
          develop
        * feature/feature2
          master
        ```

1. `git flow` を使用して `release` ブランチを操作する<br>
    - `release` ブランチを作成する場合<br>
        ```sh
        git flow release start ${VERSION}
        ```

        上記コマンドを実行することで、`develop` ブランチから `release/${VERSION}` のブランチが自動的に作成される

        ```sh
        $ git branch
        develop
        feature/feature2
        master
        * release/0.0.1
        ```

    - `release` ブランチを `develop` ブランチと `master` ブランチに merge する場合
        ```sh
        git add .
        git commit -m "a"
        git flow release finish ${VERSION}
        ```

        上記コマンドを実行することで、以下の操作が一括で行われる
        - release ブランチを master ブランチに merge
        - release ブランチを develop ブランチに merge 
        - release ブランチの削除

        ```sh
        $ git branch
        
        ```


## ■ 参考サイト
- https://qiita.com/KosukeSone/items/514dd24828b485c69a05