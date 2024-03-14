# Netlify を使用して簡単なウェブサイトをホスティングする（GitHub レポジトリの連携で行う場合）

Netlify は、静的な Web サイトのホスティングツールで、Netlify を使用すれば、静的な Web サイトか簡単にホスティングして公開することができる

Netlify でホスティングする Web アプリの GitHub レポジトリは、以下に保管しています
- https://github.com/Yagami360/netlify-app-exercise

## 使用方法

1. Web サイトの GitHub レポジトリを作成する<br>
    Netlify でホスティングするための Web サイトの GitHub レポジトリを作成する<br>
    今回は [`netlify-app-exercise`](https://github.com/Yagami360/netlify-app-exercise) という名前のレポジトリを作成している。

1. Web サイトのコードを作成する<br>
    今回は、簡単のため以下のような HTML ファイル `index.html` を直接作成する
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>netlify-app-exercise</title>
    </head>
    <body>
        <p>Hello World</p>
    </body>
    </html>
    ```

1. Netlify アカウント作成を行う<br>
    「[Netlify の Web ページ](https://www.netlify.com/)」からアカウント作成を行う。

1. Netlify コンソール UI から GitHub レポジトリの連携を行う。<br>
    アカウント登録後、マイページから対象 GitHub レポジトリの連携を行う。<br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/a6060e67-3323-43c4-b270-17aba0c6413d"><br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/ae707e40-a890-4cd8-973a-f83ef5b3b213"><br>
    <img width="300" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/9fa7d240-6343-4677-bb77-f6764481feb6"><br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/d6a0c910-adf5-4c7f-ada7-bb4c3fbb0925"><br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/d855ff4e-2bfa-4dba-ae5c-e9dc11644e53"><br>

1. デプロイ（ホスティング）された URL にアクセスする<br>
    デプロイ完了後、以下のようなページが表示されるので、<br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/cd1d437a-5ce2-4f2c-935f-cae8dd113d1e">

    デプロイ（ホスティング）された URL（今回のケースでは `https://65e7c7e6561780a750fffb5a--netlify-app-exercise.netlify.app/` にアクセスする）<br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/46e1c4d3-3bbc-49c5-a2dc-d6f9ddfb7d52"><br>

## 参加サイト

- https://qiita.com/sugo/items/2ee64887d682b0dae635