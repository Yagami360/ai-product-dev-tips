# HTML の基礎事項

## ■ xxx

- `<div>`<br>
    単体では特に意味を持たないタグだが、`<div>` で囲った部分をブロックレベル要素としてグループ化することができるタグ。`<div>` 単体だと異なる div 同士で区別がつかなくなる問題があるので、`<div class="name1">` で一意の名前をつけることが多い。

    ```html
    <html>
    ...
    <body>
        <div class="box_server_url">
            <p>API サーバーの URL を指定</p>
            <input type="text" class="form-parts" name="api_url" id="api_url" size="40" maxlength="100" value="http://localhost:5000/predict">
        </div>
    </body>
    </html>
    ```

