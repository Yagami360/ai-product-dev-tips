# 【React】Creat React App を用いて React アプリをデプロイする

## ■ 方法

1. npm をインストール
	- MacOS の場合
		```sh
		# Node.jsをインストール
		$ brew install node
		```
	> npm : Node.js のパッケージを管理するコマンド

1. React プロジェクトを作成する
  Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する
  ```sh
  $ npx create-react-app ${PROJECT_NAME}
  ```
  ```sh
  # 強制 yes にする場合
  $ npx -y create-react-app ${PROJECT_NAME}
  ```

	上記コマンドでプロジェクトを作成すると、以下のようなディレクトリ構造で各種ファイルが出力される。

	```sh
	+ ${PROJECT_NAME} + /public         			# HTML や CSS などの公開ファイル
	|                 +-- index.html    			# 表示される Web サイト。
	|                 + /src            			# React が作成した各種ソースファイル
	|                 + /node_modules         # npm のモジュール群  
	|                 + package.json          # npm でのパッケージ管理情報
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

<!--
1. デプロイしたアプリの Web サイトにアクセスする
	```sh
	$ open http://localhost:3000
	```
-->
