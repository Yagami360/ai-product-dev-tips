# 【シェルスクリプト】画像ファイルの解像度を確認する。

## 機械学習の文脈での用途
- 機械学習タスクでは、動作検証目的のための画像解像度の確認に、大量の画像ファイルをいちいちローカルに落としてきて画像解像度を確認するやり方では、時間がかかって非効率になるケースが多々存在する。
- このような場合は、サーバー上で直接画像の解像度を確認できれば便利で効率的である。

## 実現方法
このような用途として、画像の解像度を確認するUNIXコマンドは以下のようになる。

```sh
$ file ${image_file_name}
```

```sh
[例]
$ file image01.png
> image01.png: PNG image data, 1920 x 1080, 8-bit/color RGB, non-interlaced
→ 画像解像度：1920 x 1080
```

- ディレクトリ内の全画像の解像度確認
    ```sh
    # * はワイルドカードで、0文字以上の任意の文字を表す。
    $ file *

    > Icon:                                directory
    > SHOT NOTE:                           directory
    > お気に入り:                          directory
    > アップロード:                        directory
    > カメラロール:                        directory
    > はてなブログトレンド_測度論１.png:   PNG image data, 1920 x 1080, 8-bit/color RGB, non-interlaced
    > はてなブログトレンド_測度論２.png:   PNG image data, 1920 x 1080, 8-bit/color RGB, non-interlaced
    > はてなブログトレンド_関数解析１.png: PNG image data, 1920 x 1080, 8-bit/color RGB, non-interlaced
    > はてなブログトレンド_関数解析２.png: PNG image data, 1920 x 1080, 8-bit/color RGB, non-interlaced
    ```

- ディレクトリ内の PNG ファイルのみ解像度確認
    ```sh
    $ file *.png
    ```

- ディレクトリ内の PNG と JPEG ファイルのみ解像度確認
    ```sh
    $ file *.png *.jpg
    ```
