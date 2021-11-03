# 【React】React Hooks でステートフックを永続化する

データの永続化を行っていないアプリでは、ブラウザでアプリのページをリロードすると、入力したデータなどがすべて消えてしまう。

React Hooks を利用した React アプリにおいては、ローカルストレージにアプリのデータを保存する方法が、最も手軽に永続化を行うことが出来る。

この際に、ローカルストレージにデータを保存する独自フックを作成しておけば、汎用性に使えて便利である

> Redux における Redux Persist のようなデータ永続化機能は、React Hooks にはないことに注意

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
	$ npx create-react-app ${PROJECT_NAME}
	```
	```sh
	# 強制 yes にする場合
	$ npx -y create-react-app ${PROJECT_NAME}
	```

1. `src/App.js` を修正する<br>
  ```js
  ```

  ポイントは、以下の通り

  - xxx

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
