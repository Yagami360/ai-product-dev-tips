# 【Vue.js】Vue.js の基礎事項

Vue.js の使用方法には、以下の２種類が存在する

1. CDN 版（スタンドアロン版）の Vue.js を用いた方法<br>
    
    HTMLファイルに scriptタグ `<script src="https://unpkg.com/vue@next"></script>` を埋め込むだけで使えるようになる Vue.js

2. CDN 版（スタンドアロン版）の Vue.js　を用いず、`vue-cli` コマンドでデプロイする方法<br>

    - vue ファイル<br>
        html・JavaScript・CSSを一つのファイルにまとめたもの。
        公式には SFC [Single File Component] と呼ばれている


    - webpack<br>
        依存関係にある複数の Javescript ファイルを結合して、一つの「build.js」という JS ファイルを出力するようなもの（＝モジュールハンドラ）<br>
        `vue-cli` も、html・JavaScript・CSSを vue ファイル にまとめるとき、内部でこの webpack を使用している


## ■ 用語

- DOM [Document Object Model]
    HTML や XML 文書のように、

## ■ 参考サイト
- https://scrapbox.io/vue-yawaraka/%E5%88%9D%E5%BF%83%E8%80%85%E3%81%AF.vue%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%8B%E3%82%89%E5%A7%8B%E3%82%81%E3%82%8B%E3%81%B9%E3%81%8D%EF%BC%9F