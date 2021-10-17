# 【React】クラスコンポーネントを使用する

React におけるコンポーネントは、以下の形式で定義することで、オブジェクト指向におけるクラスに対しても定義することができる

```js
// React.Component はコンポーネントの基本機能を定義したクラス。これを継承することでコンポーネントクラスを定義する
class コンポーネント名 extends React.Component {
    ...

    // render() メソッドは、必ず定義する必要がある
    render(){
        return JSX形式;
    }
};
```

## ■ 方法

1. HTML ファイルを作成する
  ```html
  ```

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
	```sh
	$ open index.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="" width="500"><br>
