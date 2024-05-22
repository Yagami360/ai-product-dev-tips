# stlite を使用して Streamlit アプリをサーバレスで動作させる

「[Streamlit を使用して簡単なウェブサイトを作成する（GitHub レポジトリの連携で行う場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/48)」の項目では、Streamlit Cloud を使用して Streamlit アプリをホスティングする方法を紹介しているが、サードパーティ製の Streamlit Cloud を使用するので、セキュリティ上の懸念があり、また独自の認証認可が行えないといった問題がある。

[stlite](https://github.com/whitphx/stlite) は、xxx


## 使用方法

1. streamlit をインストールする<br>
    ```sh
    pip3 install streamlit
    ```

1. Streamlit アプリの Python コードを作成する<br>
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


1. 静的サイトの `index.html` に stlite を埋め込む
    - `index.html`
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8" />
            <meta http-equiv="X-UA-Compatible" content="IE=edge" />
            <meta
            name="viewport"
            content="width=device-width, initial-scale=1, shrink-to-fit=no"
            />
            <title>stlite app</title>
            <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.34.0/build/stlite.css"
            />
        </head>
        <body>
            <div id="root"></div>
            <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.34.0/build/stlite.js"></script>
            <script>
            fetch("streamlit_app.py")
                .then((response) => response.text())
                .then(
                    (app) => stlite.mount(
                        {
                            requirements: ["matplotlib"],     // Packages to install　
                            entrypoint: "streamlit_app.py",   // The target file of the `streamlit run` command
                            files: {
                                "streamlit_app.py": app
                            }
                        },
                        document.getElementById("root")
                    )
                );
            </script>
        </body>
        </html>
        ```

    ポイントは、以下の通り
    - `<script>` タグの中に `stlite.mount()` を記述し、stlite を埋め込んでいる

1. HTTP サーバーを起動する
    - `python` を使用する場合
        ```sh
        python -m http.server
        ```

1. ブラウザからアクセスする
    ```sh
    open http://localhost:8000/51/
    ```

## 参考サイト

- https://github.com/whitphx/stlite
- https://zenn.dev/fitness_densuke/articles/serverless_streamlit_stlite
