# 【React】React で Material-UI のコンポーネントを使用する（TypeScript 使用）

Material-UI は、Google が公開している [Material Design](https://material.io/design) というガイドラインに従ってデザインされた、React ライブラリである。

Material Design は、「こういった場合はマージンを16pxにして、こちらの場合では72pxにする」や「こういった部品を作る際は高さを56pxにする」といった具合に定量的なデザイン基準や用意すべきUI部品（コンポーネント）の種類や名前、どのようなカスタマイズを実施すべきかといった項目などの仕様化を行っており、Material-UI を使えば、この Material Design の仕様に沿った GUI 画面を作成できるようになる。

ここでは、TypeScript での React アプリで Material-UI のコンポーネントを使用する方法を記載する

> Material-UI は、JavaScript でも使えることに注意

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

<!--
1. ルーティング用パッケージをインストールする<br>
  ルーティング（＝別ページへのリンクやリダイレクトなど）用パッケージ
  ```sh
  npm install --save react-router-dom                       # ルーティング（リダイレクト）用パッケージ
  npm install --save-dev @types/react-router-dom            # ルーティング（リダイレクト）用パッケージ
  ```
  > 後述の Material-UI のテンプレート集コード内で上記パッケージを使用しているのでインストールが必要
-->

1. Material-UI をインストールする<br>
  ```sh
  $ cd ${ROOT_DIR}/${PROJECT_NAME}
  $ npm install --save @material-ui/core @material-ui/icons
  ```

1. フォントを導入する<br>
  `public/index.html` に以下の `<link>` タグを追加し、Material-UI と相性の良いGoogle日本語フォントとフォントアイコンを導入する<br>

  ```html
  <head>
    ...
    <!-- Material-UI と相性の良いGoogle日本語フォントとフォントアイコンを CDN で導入する -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Noto+Sans+JP&subset=japanese" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
    ...
  </head>
  ```

<!--
1. Material-UI のテンプレート集から気に入ったテンプレートのソースファイルをコピペする。
  [Material-UIが公開しているテンプレート集](https://mui.com/getting-started/templates/) から、気に入ったテンプレートのソースファイルをコピペする。<br>
  ここでは、`src/Components/.tsx` にテンプレートのコードをコピペする

  ```tsx
  ```
-->

1. `src/App.js` を修正する<br>
    ```js
    import React from "react";
    import Typography from '@material-ui/core/Typography';    // 文字表示を表現できるコンポーネント。文字位置や文字色、どのタグ（h1など）とするか、どのタグのスタイルをあてるかなどを設定できる。
    import Button from '@material-ui/core/Button';
    import IconButton from '@material-ui/core/IconButton';
    import AppBar from '@material-ui/core/AppBar';            // ナビゲーションバー
    import Toolbar from '@material-ui/core/Toolbar';          // ナビゲーションバー
    import MenuIcon from '@material-ui/icons/Menu';           // メニューコンポーネント群。Buttonと組み合わせて、クリックされたときにメニューを開くといったように使う。
    import { useTheme } from '@material-ui/core/styles';
    import { ThemeProvider　} from '@material-ui/core/styles';

    // React.VFC : React に関数コンポーネントの型（VFC : Void Function Component）
    const App: React.VFC = () => {
      // useTheme() でテーマ（画面全体のスタイル）のオブジェクトを作成
      const theme = useTheme();

      // <ThemeProvider> コンポーネントの theme 属性に useTheme() で作成した theme オブジェクトを設定し、他の Material-UI コンポーネントを包むことでテーマを適用出来る（※ theme オブジェクトの各属性（theme.palette など）を各コンポーネントの style 属性に設定することでもテーマのスタイルを適用できる）
      // 各 Material UI コンポーネントの variant 属性 : 各コンポーネント毎に定義された表示バリエーションを定義（例えば、ボタンコンポーネントの場合は "outlined", "contained" などがある）
      // 各 Material UI コンポーネントの color 属性 : primary or secondary と呼ばれる2つの色を定義
      return (
        <ThemeProvider theme={theme}>
          <AppBar position="static">
            <Toolbar>
              <IconButton edge="start" color="inherit" aria-label="menu">
                <MenuIcon />
              </IconButton>
              <Typography variant="h6">Material UI Sample App</Typography>
            </Toolbar>        
          </AppBar>
          <Button variant="contained">contained</Button>
          <Button variant="outlined">outlined</Button>
          <Button variant="contained" color="primary">primary</Button>
          <Button variant="contained" color="secondary">secondary</Button>
        </ThemeProvider>
      );
    };

    export default App;

    ```

    ポイントは、以下の通り

    - 基本的に `material-ui/core` 以下のコンポーネントを import することで、各 UI（ボタンなど）のコンポーネントを使えるようになる。

    - 各 Material UI コンポーネントの `variant` 属性で、各コンポーネント毎に定義された表示バリエーションを定義できる。例えば、ボタンコンポーネントの場合は `"contained"`, `"outlined"` などがある
      ```js
      <Button variant="contained">contained</Button>
      <Button variant="outlined">outlined</Button>
      ```
      <img src="https://user-images.githubusercontent.com/25688193/141604655-1f739293-6454-488b-bd4d-9797c979c675.png" width="300"><br>

    - 各 Material UI コンポーネントの color 属性で、`"primary"` or `"secondary"` と呼ばれる2つの色を定義できる<br>
      ```js
      <Button variant="contained" color="primary">primary</Button>
      <Button variant="contained" color="secondary">secondary</Button>
      ```
      <img src="https://user-images.githubusercontent.com/25688193/141604524-aa4c90f7-86b0-4ef7-8d5a-2c9be40051b1.png" width="300"><br>

    - Material-UI の `<ThemeProvider>` コンポーネントの `theme` 属性に `useTheme()` で作成した `theme` オブジェクトを設定し、他の Material-UI コンポーネントを包むことでテーマを適用出来る
    
      > `theme` オブジェクトの各属性（`theme.palette` など）を各 Material-UI コンポーネントの `style` 属性に設定することでもテーマのスタイルを適用できる
      > ```jsx
      > <Button variant="contained" style={{ backgroundColor: theme.palette.primary.light }}>
      > ```

    - 今回使用している各種 Material-UI のコンポーネントは、以下のようなもの（他にも多数のコンポーネントがある）<br>
      - `Typography` : 文字表示を表現できるコンポーネント。文字位置や文字色、どのタグ（h1など）とするか、どのタグのスタイルをあてるかなどを設定できる。
      - `Button` : 入力ボタン
      - ナビゲーションバー関連<br>
        <img src="https://user-images.githubusercontent.com/25688193/141605002-e519c468-52ec-4b33-8432-c2af4310a0f3.png" width="500"><br>
        - `AppBar` : ナビゲーションバーの全体
        - `Toolbar` : ナビゲーションバー。`<AppBar>` と組み合わせて使用する？
        - `IconButton` : 
        - `MenuIcon` : ナビゲーションバーでよく使われる「≡」アイコン
          
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
- https://qiita.com/h-yoshikawa44/items/efa33101b0a02cba7759
- https://dev.classmethod.jp/articles/react-material-ui/
