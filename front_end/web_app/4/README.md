# JavaScript の基礎事項

## ■ 一般事項

- document
    HTML の要素へ javascript からアクセスするには、`document` オブジェクトを使用すればよい

    - 例：head要素の中身を出力
        ```javascript
        console.log( document.head );
        ```

    - 例：body要素の中身を出力
        ```javascript
        //body要素の中身を出力
        console.log( document.body );
        ```

    - 例：id 値に一致する内容を出力
        ```javascript
        console.log( document.getElementById('id_1'); );
        ```

## ■ jQuery

- `$(function() {...})`
    HTML の読み込みが全て完了した後に JavaScript `***.js` が実行されるようにするためには `$(function(){...});` で処理を定義すればよい

    ```javascript
    $(function(){
        // 処理
    });
    ```

    ```javascript
    jQuery(function(){
        // 処理
    });
    ```

- 変数定義
    jQuery で生成されたオブジェクト変数に `$` を付けるのが作法
    ```javascript
    $(function(){
        var $pose_selectPanel;
    });
    ```

- セレクタ
    jQuery には、HTML ファイル内の要素を指定するためのセレクタと呼ばれる機能が用意されている。

    - 例：`<body>` タグ内の全ての `<img>` タグにアクセス
        ```javascript
        $("img")
        ```
    - 例：`<body>` タグ内の id 値が `id_image1` の `<img>` タグにアクセス
        ```javascript
        $("img#id_image1")
        ```
    - 例：`<body>` タグ内の class 名が `class_image1` の要素にアクセス
        ```javascript
        $(".class_image1")
        ```


- jQuery での Ajax通信

