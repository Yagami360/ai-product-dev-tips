# 【Vue.js】コンポーネントでイベント処理する（CDN 版での構成）

## ■ v-on 属性を使用して、ボタンクリックイベントをコンポーネントに割り当てる（バインドする）

Javascript でボタンクリックのイベントを検出したい場合は、`<input type="button" value="button" onclick="buttonClick()">` のように、`<input>` タグの `onclick` 属性を利用するが、
この方法だと、コンポーネント内で定義した変数に `{{変数名}}` の形式でアクセスできなくなってしまう。

そのため、Vue.js でイベント処理を行う場合は、v-on 属性を使用して、イベントをコンポーネントに割り当てて、イベント処理を行うことになる。



v-on 属性の構文は、以下のようになる。

```js
v-on:${イベント属性名から on を取り除いた名前} = "イベント処理"
```
```js
# 例 : `onclick` 属性（ボタンクリック）のイベントの場合
v-on:click = "イベント処理"
```

イベント発生時のイベント処理は、以下のようにコンポーネントに `method` プロパティを用意して処理内容を記述する形式になる

```js
let app = Vue.createApp(appdata)
app.component('コンポーネント名', {
  data() {
    return {
      ...
    }
  },
  // method プロパティでイベント処理を実装
  methods:{
    メソッド名１(event) {
      ...
    },
    メソッド名２(event) {
      ...
    },
    ...
  },
})
```

### ◎ 方法

1. Vue.js を用いた静的な Web ファイル `index1.html` を作成する
	```html
  <!DOCTYPE html>
  <html>
  <head>
    <title>My first Vue app</title>
    <script src="https://unpkg.com/vue@next"></script>
  </head>

  <body>
    <h1 class="bg-secondary text-white display-4 px-3">Vue3</h1>
    <div id="app" class="container">
      <p>{{ message }}</p>
      <!-- <コンポーネント名 /> でコンポーネントを使用 -->
      <div><counter_component /></div>		
    </div>
    
    <script>
    const appdata = {
      data() {
        return {
          message : 'コンポーネントを表示する',
        }
      }
    }
    
    // アプリケーションオブジェクトの変数定義
    let app = Vue.createApp(appdata)
    
    // コンポーネントの作成 : app.component(コンポーネント名、{設定情報})
    app.component('counter_component', {
      // data() メソッドでコンポーネント内で使用する変数を定義できる
      data() {
        return {
          counter: 0,
        }
      },
      // methods プロパティでイベント処理を実装
      methods:{
        increment_counter() {
          this.counter++
        },
      },
      // {設定情報} の `template:` 項目に設定した内容がコンポーネントとして表示される
      //template: '<input type="button" value="button" onclick="counter++"></input><p>clicked: {{counter}}.</p>'						// onclick 属性をそのまま使用すると、コンポーネント内の変数 counter に {{counter}} でアクセスできなくなる
      template: '<input type="button" value="button" v-on:click="increment_counter"></input><p>clicked: {{counter}}.</p>'		// v-on 属性で onclick イベントを割り当てることで、コンポーネント内の変数 counter に {{counter}} でアクセスできる
    })
    app.mount('#app')
    </script>
  </body>

  </html>
	```

	ポイントは、以下の通り

	- xxx

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index1.html
	```

