# Kedro を使用して簡単なワークフローを構成する

Kedro は、Airflow と同じく Python スクリプトで動作するパイプラインツールである。

Kedro は、以下のようなコンポーネントから構成される

- DataCatalog<br>
    Pipeline で使用するデータを定義した yaml ファイル

- Pipeline<br>
    Node の依存関係や実行順序を管理して一連の処理（パイプライン）にしたもの

- Node<br>
    実行される処理の単位で、前処理や学習といった処理本体になるもの。
    Pipeline は、複数の一連の Node を連結して構成される

- Runner<br>
    パイプラインを実行するもの。パラメーターを指定して実行することができ、例えば特定のパイプラインだけ実行するとかもできる。

## ■ 方法

1. Kedro をインストールする<br>
    ```sh
    pip install kedro
    pip install kedro-viz
    ```

1. Kedro プロジェクトを作成する<br>

    - プロジェクトのコンフィグファイルを使用しない場合
        - 空のプロジェクトを作成する場合
            ```sh
            kedro new
            ```

        - テンプレートありでプロジェクトを作成する場合
            ```sh
            kedro new --starter=pandas-iris
            ```

            > `--starter=pandas-iris` : iris データセットでモデルを動かすためのパイプラインやノード、データカタログがテンプレートとして自動的に用意される

        上記コマンド実行後、プロジェクト名等との確認メッセージが出力されるので、名前を設定後 Enter キーを押す
        ```sh
        Project Name:
        =============
        Please enter a human readable name for your new project.
        Spaces and punctuation are allowed.
        [New Kedro Project]: kedro_project

        Repository Name:
        ================
        Please enter a directory name for your new project repository.
        Alphanumeric characters, hyphens and underscores are allowed.
        Lowercase is recommended.
        [kedro_project]: 

        Python Package Name:
        ====================
        Please enter a valid Python package name for your project package.
        Alphanumeric characters and underscores are allowed.
        Lowercase is recommended. Package name must start with a letter
        or underscore.
        [kedro_project]: 
        ```


    - プロジェクトのコンフィグファイルを使用する場合<br>
        `config.yml` からプロジェクトを作成することもできる

        1. `config.yml` を作成する
            ```yaml
            #output_dir: ~/code
            project_name: kedro_project
            repo_name: kedro_project
            python_package: kedro_project
            ```

        1. プロジェクトを作成する
            - 空のプロジェクトを作成する場合
                ```sh
                kedro new --config config.yml
                ```

            - テンプレートありでプロジェクトを作成する場合
                ```sh
                kedro new --config config.yml --starter=pandas-iris
                ```

1. 作成した Redro プロジェクトの依存関係をインストールする<br>
    ```sh
    cd ${KEDRO_PROJECT_NAME}
    kedro install
    ```

    > 上記コマンドにより、`${KEDRO_PROJECT_NAME}/src/requirements.txt` の内容に従って、各種 Python ライブラリがインストールされる。

1. Redro でのパイプラインラインのコードを作成する<br>
    1. DataCatalog を作成する<br>
        学習用データセットなどの Node（Pipeline 中の実行される処理の単位）で使用する入力データは、DataCatalog と呼ばれる `conf/base/catalog.yml` ファイルを編集して行う。

        ```yaml
        example_iris_data:
          type: pandas.CSVDataSet
          filepath: data/01_raw/iris.csv
        ```

        複数の入力データがある場合や csv 以外のデータの場合は、例えば以下のように記述すればよい。

        ```yaml
        example_iris_csv_data:
          type: pandas.CSVDataSet
          filepath: data/01_raw/iris.csv

        example_iris_pickle_data:
          type: pickle.PickleDataSet
          filepath: data/01_raw/iris.pickle
          backend: pickl
        ```

        > `data/01_raw` ディレクトリには、生データを保管

        > 今回は、テンプレートと同じ iris データを使用するので、テンプレートで作成された `catalog.yml` をそのまま使用する

    1. Node を修正する<br>
        Pipeline 中の実行される処理の単位である Node は、`src/${KEDRO_PROJECT_NAME}/pipelines/nodes.py` に記載する

        > 今回の iris テンプレートでは、`src/${KEDRO_PROJECT_NAME}/pipelines/data_engineering/nodes.py` と `src/${KEDRO_PROJECT_NAME}/pipelines/data_science/nodes.py` の２つが存在する

        > 今回は、テンプレートと同じ `nodes.py` をそのまま使用する

        - `pipelines/data_engineering/nodes.py`
            ```python
            from typing import Any, Dict
            import pandas as pd

            def split_data(data: pd.DataFrame, example_test_data_ratio: float) -> Dict[str, Any]:
                """Node for splitting the classical Iris data set into training and test
                sets, each split into features and labels.
                The split ratio parameter is taken from conf/project/parameters.yml.
                The data and the parameters will be loaded and provided to your function
                automatically when the pipeline is executed and it is time to run this node.
                """
                data.columns = [
                    "sepal_length",
                    "sepal_width",
                    "petal_length",
                    "petal_width",
                    "target",
                ]
                classes = sorted(data["target"].unique())
                # One-hot encoding for the target variable
                data = pd.get_dummies(data, columns=["target"], prefix="", prefix_sep="")

                # Shuffle all the data
                data = data.sample(frac=1).reset_index(drop=True)

                # Split to training and testing data
                n = data.shape[0]
                n_test = int(n * example_test_data_ratio)
                training_data = data.iloc[n_test:, :].reset_index(drop=True)
                test_data = data.iloc[:n_test, :].reset_index(drop=True)

                # Split the data to features and labels
                train_data_x = training_data.loc[:, "sepal_length":"petal_width"]
                train_data_y = training_data[classes]
                test_data_x = test_data.loc[:, "sepal_length":"petal_width"]
                test_data_y = test_data[classes]

                # When returning many variables, it is a good practice to give them names:
                return dict(
                    train_x=train_data_x,
                    train_y=train_data_y,
                    test_x=test_data_x,
                    test_y=test_data_y,
                )
            ```

            ポイントは、以下の通り

            - `split_data` メソッドの `data` 引数に、DataCatalog `catalog.yml` で指定した iris 学習用データセットが入力されている

            - この Node の処理内容としては、iris データセットを学習用データセットとテスト用データセットに分割する処理になっている。

    1. Pipeline を作成する<br>
        Pipeline のコードは、`src/${KEDRO_PROJECT_NAME}/pipelines/pipeline.py` に記載する

        > 今回の iris テンプレートでは、`src/${KEDRO_PROJECT_NAME}/pipelines/data_engineering/pipeline.py` と `src/${KEDRO_PROJECT_NAME}/pipelines/data_science/pipeline.py` の２つが存在する

        > 今回は、テンプレートと同じ `pipeline.py` を使用する

        - `pipelines/data_engineering/pipeline.py`
            ```python
            from kedro.pipeline import node, pipeline
            from .nodes import split_data

            def create_pipeline(**kwargs):
                return pipeline(
                    [
                        node(
                            split_data,     # Node を定義したメソッド `split_data(...)` メソッドを設定
                            ["example_iris_data", "params:example_test_data_ratio"],
                            dict(
                                train_x="example_train_x",
                                train_y="example_train_y",
                                test_x="example_test_x",
                                test_y="example_test_y",
                            ),
                            name="split",
                        )
                    ]
                )
            ```

            ポイントは、以下の通り

            - `create_pipeline()` メソッドは、 `kedro.pipeline.pipeline()` メソッドを return する。この時 `kedro.pipeline.pipeline()` メソッドの引数には、`kedro.pipeline.node()` メソッドのリストを設定し、更に `kedro.pipeline.node()` メソッドの引数に、前述の Node を定義したメソッド `split_data(...)` メソッドを設定することで、Pipeline を構成している

            - 今回の例では、`kedro.pipeline.pipeline()` メソッドの引数に設定している `kedro.pipeline.node()` メソッドは１つであるが、複数の Node から構成される Pipeline の場合は、複数の `kedro.pipeline.node()` をリスト形式で設定すればよい

    1. Hooks を作成する<br>

        `src/${KEDRO_PROJECT_NAME}/hooks.py` に記載する

1. Redro を実行する<br>
    ```sh
    kedro run
    ```

    > 実行結果は、`logs` ディレクトリに保管される

1. kedro-viz で Pipeline を可視化する<br>
    ```sh
    kedro viz --host 0.0.0.0
    ```
    > 上記コマンド実行後、`http://0.0.0.0:4141/` に自動的にブラウザアクセスできる

    <img width="1000" alt="image" src="https://user-images.githubusercontent.com/25688193/172851590-64eeead9-8a61-4f69-a3d6-d570a5ca2fad.png">


## ■ 参考サイト

- https://www.st-hakky-blog.com/entry/2020/11/27/120000
- https://qiita.com/nokoxxx1212/items/2395d3a3dbcd9410e5e7
- https://qiita.com/ozora/items/b06011faa3145bb66271