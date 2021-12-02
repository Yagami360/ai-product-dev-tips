# 【React】React Router で複数ページの React アプリを作成する

## ■ 方法

1. npm をインストール
	- MacOS の場合
		```sh
		# Node.jsをインストール
		$ brew install node
		```
	> npm : Node.js のパッケージを管理するコマンド

1. React プロジェクトを作成する<br>
  Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する

	```sh
	# 強制 yes にする場合
	$ npx -y create-react-app ${PROJECT_NAME} --template typescript 
	```

  > 今回は TypeScript での React アプリを作成するので、`--template typescript` を設定している

1. ルーティング用パッケージをインストールする<br>
  ルーティング（＝別ページへのリンクやリダイレクトなど）用パッケージをインストールする
  ```sh
  npm install --save react-router-dom                       # ルーティング（リダイレクト）用パッケージ
  npm install --save-dev @types/react-router-dom            # ルーティング（リダイレクト）用パッケージ
  ```

  > 現時点では 、上記コマンドで version6 の React-Router がインタフェースされる
  
  > version5 -> version6 の更新でインタフェースが大きく変わっていることに注意

1. `src/App.js` を修正する<br>
    ```js
    import React from 'react';
    import { BrowserRouter, Route, Routes } from 'react-router-dom';
    import { Link } from "react-router-dom";
    import './App.css';
    import HomePage from './pages/HomePage'
    import AboutPage from './pages/AboutPage'

    const App: React.FC = () => {
      return (
        <BrowserRouter>
          {/* ルーティング設定 */}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
          { /* リスト */}
          <ul>
            <li>
              <Link to="/">Home</Link>          {/* 別ページへのリンク */}
            </li>
            <li>
              <Link to="/about">About</Link>    {/* 別ページへのリンク */}
            </li>
          </ul>
        </BrowserRouter>
        );
    }

    export default App;
    ```

    ポイントは、以下の通り

    - 上記は version 6.x の React-Router の書き方になっている。version5 -> version6 の更新でインタフェースが大きく変わっていることに注意

    - React アプリにおいて、複数ページへのアクセスを可能にするためには、まずはじめに `http://localhost:3000/home` にアクセスしたら HomePage のコンポーネントを表示し、`http://localhost:3000/about` にアクセスしたら AboutPage のコンポーネントを表示するといった具合に、各コンポーネントとアドレスの紐付け（＝ルーティング）を必要がある。このルーティングは、以下の処理で行うことが出来る。
      1. `<BrowserRouter>` コンポーネントでアプリ全体を包む
      1. `<Routes>` コンポーネントで各ページの `<Route>` コンポーネントを包む
      1. `<Route>` コンポーネントで URL と各ページのコンポーネントのルーティングを行う。具体的には、`path` 属性で URL を設定し、`element` 属性でその URL で表示するコンポーネントを設定する<br>

      > この例では、HomePage コンポーネントの URL を App コンポーネントの URL と同じ `/` にしているので、HomePage のルーティングを行った時点で、HomePage コンポーネントの内容が表示されることに注意

    - ページリンクを作成したい場合は、`<Link>` コンポーネントの `to` 属性に、上記ルーティングを行った URL を設定すればいよい
    
      > この時 `<Link>` コンポーネントは `<BrowserRouter>` コンポーネント内で呼び出す必要があることに注意


1. 別ページのコンポーネントを作成する<br>
   - `pages/HomePage.tsx`
      ```tsx
      import React from 'react';

      const HomePage: React.VFC = () => {
        return (
          <h1>Home Page</h1>
        );
      }

      export default HomePage;
      ```

   - `pages/HomePage.tsx`
      ```tsx
      import React from 'react';

      const AboutPage: React.VFC = () => {
        return (
          <h1>About</h1>
        );
      }

      export default AboutPage;
      ```

1. 【オプション】プロジェクトをビルドする
	React を用いたアプリケーションを公開したい場合は、以下のコマンドでプロジェクトをビルドして公開する
	```sh
	$ npm run build
	```

	> ビルドしたプロジェクトは `${PROJECT_NAME}/build` ディレクトリに作成される。この build ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

1. 作成した React のプロジェクトのサーバーを起動する
	```sh
	$ cd ${PROJECT_NAME}
	$ npm start
	```

	コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く


## ■ 参考サイト

- version 6.x
  - https://qiita.com/junjis0203/items/0096963aefb70f466c27

- version 5.x
  - https://reffect.co.jp/react/react-router