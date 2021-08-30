# 【Python】ffmpeg を使用して画像ファイルと音声ファイル（mp3）から動画ファイル（mp4）を作成する

## 方法１（ffmpegコマンドでシェルスクリプトから行う場合）

1. ffmpeg コマンドをインストールする
    - MacOS の場合
        ```sh
        $ brew install ffmpeg
        ```
    - Ubuntu の場合
        ```sh
        $ sudo apt install ffmpeg
        ```

1. ffmpeg コマンドを用いて、mp3 ファイルと画像ファイルから mp4 ファイルを作成する
    ```sh
    $ ffmpeg \
        -i ${IN_IMAGE_FILE} -i ${IN_AUDIO_FILE} \
        -map 0:v -map 1:a \
        -loop 1 \
        -framerate 1 -r ${FPS} \
        -vf "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p" \
        -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \
        ${OUT_VIDEO_FILE}
    ```
    - `-map 0:v -map 1:a` : 画像ファイル `${IN_IMAGE_FILE}` からビデオを選択し、音声ファイル `${IN_AUDIO_FILE}` からオーディオのみを選択します。これは、画像ファイル `${IN_IMAGE_FILE}` が MP3 に添付されているアルバム/カバーアートよりも小さい場合に必要。そうでない場合は、代わりにアルバム/カバーアートを選択します。
    - `-loop 1` : １枚の画像で動画ファイルが作れるようになる
    - `-framerate 1 -r 10` : `-framerate` は入力 FPS。`-r` は出力動画の FPS。入力の FPS は 1 で 出力の１FPS は 10 を推奨。<br>
        入力のFPS10fpsに設定するのに比べて、入力のFPSを1にしてして出力のFPSを10fにするほうが、フレームを複製するのが速くなり、エンコードが速くなる。またほとんどの動画プレイヤーは6fps以下では再生できません。10は安全な値。
    - `scale='iw-mod(iw,2)':'ih-mod(ih,2)` : スケールフィルタを使って、出力動画の幅と高さが2で割り切れるようにします。（２で割り切れないとエラーが発生する）
    - `format=yuv420p` : 再生互換性のために、出力に YUV 4:2:0 クロマサブサンプリングを使用
    - `-movflags +faststart` : ビデオの再生開始を速くする
    - `-shortest` : 出力動画を音声ファイル `${IN_AUDIO_FILE}` の長さにします。これは、-loop 1が使用されたために必要です。

## 方法２（ffmpeg コマンド python スクリプト内から使用して行う場合）

python の `subprocess.call(...)` を使用して、ffmpeg コマンドを直接実行する

1. 変換スクリプトを作成する
    ```python
    ```
    
1. 変換スクリプトを実行する
    ```sh
    $ sh convert_mp3_to_mp4_3.sh
    ```


## 方法３（python-ffmpeg を使用して python スクリプトから行う場合）

> [ToDo] 実装中...

1. python-ffmpeg をインストールする
    ```sh
    $ pip install ffmpeg-python
    ```

1. 変換スクリプトを作成する
    ```python
    ```
    
1. 変換スクリプトを実行する
    ```sh
    $ sh convert_mp3_to_mp4_2.sh
    ```


## ■ 参考サイト
- https://qiita.com/economist/items/bb325e8d23e0b3521c65
- https://stackoverflow.com/questions/64375367/python-convert-mp3-to-mp4-with-static-image
- https://qiita.com/studio_haneya/items/a2a6664c155cfa90ddcf
