# Streamlit を使用して簡単なウェブサイトを作成する

Streamlit を使用すれば、Python を使用して Web アプリを簡単に作成することができる。

Streamlit アプリ用の GitHub レポジトリは、以下に保管しています
- https://github.com/Yagami360/streamlit-app-exercise

## 使用方法

1. streamlit をインストールする<br>
    ```sh
    pip3 install streamlit
    ```

1. 【オプション】Streamlit デモサイトを起動する<br>
    以下のコマンドを実行することで、streamlit を使用したデモサイトがローカル環境上（`http://localhost:8501/`）で起動する
    ```sh
    streamlit hello
    ```
    <img width="600" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/f3bc5733-063f-427a-9604-239e130227c9"><br>
    <img width="600" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/ed9af929-87f6-49d3-9707-8cdc2ee2b1c9"><br>

1. Streamlit アプリ用の GitHub レポジトリを作成する
    今回は [`streamlit-app-exercise`](https://github.com/Yagami360/streamlit-app-exercise) という名前のレポジトリを作成している。

1. Streamlit アプリの Python コードを作成する<br>
    上記レポジトリにStreamlit アプリのコードを追加する。
    `streamlit_app.py` というファイル名にすると、ホスティング URL にファイル名を含めずにアクセスできる。

    - コード例１
        ```python
        x = 10
        'x: ', x 
        ```

    - コード例２
        ```python
        ```

    ポイントは、以下の通り

    - `マジックコマンド`: 

    - xxx

1. Streamlit Cloud アカウントを作成する<br>
    「[Streamlit Cloud の Web ページ](https://streamlit.io/cloud)」からアカウント登録を行う。<br>

1. Streamlit Cloud にアプリの追加を行う<br>
    ログイン後、コンソールUI 上から streamlit アプリ（GitHub レポジトリ）を追加し、デプロイ（ホスティング）する。
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/b91d7d30-d8e6-4fbe-b2d1-501c290c19c6"><br>
    <img width="300" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/3e71b8b5-0efb-416f-91c0-b623f9ae4f41"><br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/792e9e99-437d-47e5-a034-24e15ea21bec"><br>

1. デプロイ（ホスティング）された URL にアクセスする<br>
    デプロイ（ホスティング）された URL（今回のケースでは `https://app-app-exercise-srimrz7jvk9udzphvp98bs.streamlit.app/` にアクセスする）

## 参考サイト

- https://qiita.com/tamura__246/items/366b5581c03dd74f4508
