# 【GCP】Cloud Scheduler 機能を用いて、サーバーを一定の時間間隔で起動・停止する。
全体的な構成は、以下のような図となります。

<img src="/attachment/5e3cff42b4655300410883fb" width="500">

この機能を利用することにより、例えば、深夜や休日などの GCP インスタンスが使われない時間帯のみインスタンスを停止状態にし、その他の時間帯ではインスタンスを起動状態にするといったような利用が可能となります。
又、本手法と別記事「[【GCP】サーバー起動後に自動的に実行するスクリプトを設定する。](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/5)」 で紹介している方法と組み合わせることで、「GCPインスタンスを指定した時間スケジュールで起動・停止させつつ、起動時には WebAPI などを実行可能な状態にしておく」といった活用が可能となります。
    
## 1. Cloud Functions の設定

### 1-1. 起動関数の作成
1. [Cloud Functions](https://console.cloud.google.com/functions?hl=ja) ページに移動して、「関数を作成」をクリックします。
    <img src="/attachment/5e3cdd47b4655300410883d4" width="450">
    
1. 関数作成画面に移動後、以下の項目を設定します。
    <img src="/attachment/5e3cde69b4655300410883d9" width="600">
    - 名前 : startInstancePubSub
        - 画面上の名前欄には、「この名前は既に使用されています」との警告が出ていますが、これはすでにこの関数を作成済みの環境で撮影したためであり、新規に作成する場合はこのような警告は出てきません。
    - 割り当てるメモリ : 128 MB
    - トリガー : Cloud Pub/Sub
    - トピック : 「新しいトピックを作成…」をクリックし、名前に「start-instance-event」を入力
    - ソースコード : インライン エディタ
    - ランタイム : Node.js 6
        - Node.js 6 は非推奨になっていますが、[Googleの公式サイト](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja) 上に記載されている `index.js` と `package.json` のコードは、Node.js 6 で動作するようです。
        - [GitHub](https://github.com/GoogleCloudPlatform/nodejs-docs-samples/tree/master/functions/scheduleinstance) 上にある最新の `index.js` と `package.json` のコードでは、Node.js 8 に対応しているようですが、このコードで動作させると、うまくサーバー起動・
    - `index.js` タブ : 以下のコードに置きかえる。
        ```js
        const Buffer = require('safe-buffer').Buffer;
        const Compute = require('@google-cloud/compute');
        const compute = new Compute();

        /**
         * Starts a Compute Engine instance.
         *
         * Expects a PubSub message with JSON-formatted event data containing the
         * following attributes:
         *  zone - the GCP zone the instance is located in.
         *  instance - the name of the instance.
         *
         * @param {!object} event Cloud Function PubSub message event.
         * @param {!object} callback Cloud Function PubSub callback indicating completion.
         */
        exports.startInstancePubSub = (event, callback) => {
          try {
            const pubsubMessage = event.data;
            const payload = _validatePayload(
              JSON.parse(Buffer.from(pubsubMessage.data, 'base64').toString())
            );
            compute
              .zone(payload.zone)
              .vm(payload.instance)
              .start()
              .then(data => {
                // Operation pending.
                const operation = data[0];
                return operation.promise();
              })
              .then(() => {
                // Operation complete. Instance successfully started.
                const message = 'Successfully started instance ' + payload.instance;
                console.log(message);
                callback(null, message);
              })
              .catch(err => {
                console.log(err);
                callback(err);
              });
          } catch (err) {
            console.log(err);
            callback(err);
          }
        };

        /**
         * Validates that a request payload contains the expected fields.
         *
         * @param {!object} payload the request payload to validate.
         * @returns {!object} the payload object.
         */
        function _validatePayload(payload) {
          if (!payload.zone) {
            throw new Error(`Attribute 'zone' missing from payload`);
          } else if (!payload.instance) {
            throw new Error(`Attribute 'instance' missing from payload`);
          }
          return payload;
        }
        ```        
        - 注 ： ここに貼り付けたコードは、[Googleの公式サイト](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja) 上に記載されている `index.js` のコードで、ランタイム（Node.js 6）で動作します。[GitHub](https://github.com/GoogleCloudPlatform/nodejs-docs-samples/blob/master/functions/scheduleinstance/index.js) 上にある最新の `index.js` は、このコードから変更が行われており、ランタイム（Node.js 8）で動作するようになっているようです。
    - `package.json` タブ : 以下のコードに置き換える。
        ```json
        {
          "name": "cloud-functions-schedule-instance",
          "version": "0.0.1",
          "private": true,
          "license": "Apache-2.0",
          "author": "Google Inc.",
          "repository": {
            "type": "git",
            "url": "https://github.com/GoogleCloudPlatform/nodejs-docs-samples.git"
          },
          "engines": {
            "node": ">=8"
          },
          "scripts": {
            "test": "mocha test/*.test.js --timeout=20000"
          },
          "devDependencies": {
            "@google-cloud/nodejs-repo-tools": "^3.3.0",
            "mocha": "^5.2.0",
            "proxyquire": "^2.0.0",
            "sinon": "^7.0.0"
          },
          "dependencies": {
            "@google-cloud/compute": "^0.11.0",
            "safe-buffer": "^5.1.2"
          }
        }
        ```
        - 注 ： ここに貼り付けたコードは、[Googleの公式サイト](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja) 上に記載されている `package.json` のコードで、ランタイム（Node.js 6）で動作します。[GitHub](https://github.com/GoogleCloudPlatform/nodejs-docs-samples/blob/master/functions/scheduleinstance/package.json) 上にある最新の `package.json` は、このコードから変更が行われており、ランタイム（Node.js 8）で動作するようになっているようです。
    - 実行する関数 : startInstancePubSub
    - 最後に、「作成」ボタンをクリックすると、ビルドが行われ成功すれば、関数が作成されます。

### 1-1. 停止関数の作成
停止関数についても、起動関数のときと同様の手順で作成します。

1. [Cloud Functions](https://console.cloud.google.com/functions?hl=ja) ページに移動して、「関数を作成」をクリックします。
    <img src="/attachment/5e3cdd47b4655300410883d4" width="450">
1. 関数を作成画面に移動後、以下の項目を設定します。
    <img src="/attachment/5e3cfe3cb4655300410883f4" width="600">
    - 名前 : stopInstancePubSub
        - 画面上の名前欄には、「この名前は既に使用されています」との警告が出ていますが、これはすでにこの関数を作成済みの環境で撮影したためであり、新規に作成する場合はこのような警告は出てきません。
    - 割り当てるメモリ : 128 MB
    - トリガー : Cloud Pub/Sub
    - トピック : 「新しいトピックを作成…」をクリックし、名前に「stop-instance-event」を入力
    - ソースコード : インライン エディタ
    - ランタイム : Node.js 6
    - `index.js` タブ : 以下のコードに置きかえる。（※ 起動関数とは別コードになっています）
        ```js
        const Buffer = require('safe-buffer').Buffer;
        const Compute = require('@google-cloud/compute');
        const compute = new Compute();

        /**
         * Stops a Compute Engine instance.
         *
         * Expects a PubSub message with JSON-formatted event data containing the
         * following attributes:
         *  zone - the GCP zone the instance is located in.
         *  instance - the name of the instance.
         *
         * @param {!object} event Cloud Function PubSub message event.
         * @param {!object} callback Cloud Function PubSub callback indicating completion.
         */
        exports.stopInstancePubSub = (event, callback) => {
          try {
            const pubsubMessage = event.data;
            const payload = _validatePayload(
              JSON.parse(Buffer.from(pubsubMessage.data, 'base64').toString())
            );
            compute
              .zone(payload.zone)
              .vm(payload.instance)
              .stop()
              .then(data => {
                // Operation pending.
                const operation = data[0];
                return operation.promise();
              })
              .then(() => {
                // Operation complete. Instance successfully stopped.
                const message = 'Successfully stopped instance ' + payload.instance;
                console.log(message);
                callback(null, message);
              })
              .catch(err => {
                console.log(err);
                callback(err);
              });
          } catch (err) {
            console.log(err);
            callback(err);
          }
        };

        /**
         * Validates that a request payload contains the expected fields.
         *
         * @param {!object} payload the request payload to validate.
         * @returns {!object} the payload object.
         */
        function _validatePayload(payload) {
          if (!payload.zone) {
            throw new Error(`Attribute 'zone' missing from payload`);
          } else if (!payload.instance) {
            throw new Error(`Attribute 'instance' missing from payload`);
          }
          return payload;
        }
        ```
    - `package.json` タブ : 以下のコードに置き換える。
        ```json
        {
          "name": "cloud-functions-schedule-instance",
          "version": "0.0.1",
          "private": true,
          "license": "Apache-2.0",
          "author": "Google Inc.",
          "repository": {
            "type": "git",
            "url": "https://github.com/GoogleCloudPlatform/nodejs-docs-samples.git"
          },
          "engines": {
            "node": ">=8"
          },
          "scripts": {
            "test": "mocha test/*.test.js --timeout=20000"
          },
          "devDependencies": {
            "@google-cloud/nodejs-repo-tools": "^3.3.0",
            "mocha": "^5.2.0",
            "proxyquire": "^2.0.0",
            "sinon": "^7.0.0"
          },
          "dependencies": {
            "@google-cloud/compute": "^0.11.0",
            "safe-buffer": "^5.1.2"
          }
        }
        ```
    - 実行する関数 : stopInstancePubSub
    - 最後に「作成」ボタンをクリックすると、ビルドが行われ成功すれば、関数が作成されます。

起動関数と停止関数が正常に作成されれば、Cloud Functions 上の画面に以下のような２つの関数 `startInstancePubSub`, `stopInstancePubSub` が追加されています。
![image.png](/attachment/5e3ce278b4655300410883dc)

## 2. Cloud Scheduler の作成

### 2.1 起動ジョブ作成
1. [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler?hl=ja) ページに移動して、「ジョブを作成」をクリックします。
    <img src="/attachment/5e3ce57ab4655300410883df" width="450">
1. ジョブの作成画面の以下の項目を設定します。
    <img src="/attachment/5e3ce92cb4655300410883e1" width="400">
    - 名前 : startup-workday-instance
        - 画面上の名前欄には、「この名前は既に使用されています」との警告が出ていますが、これはすでにこのジョブ作成済みの環境で撮影したためであり、新規に作成する場合はこのような警告は出てきません。
    - 頻度 : ジョブの実行頻度を cron 形式で入力します。
        - cron 形式は、以下の画像のようなフォーマットをしています。例えば、上記画面では、「毎日午前９時」に、この起動ジョブが実行される設定になっています。この値をカスタマイズすることで、インスタンスの起動時間を任意に指定することが可能になります。
        <img src="/attachment/5e3ce956b4655300410883e2" width="230">
    - タイムゾーン : 日本時間で指定したければ、「日本標準時（JST）」を指定します。
    - ターゲット : Pub/Sub
    - トピック : start-instance-event
    - ペイロード : 上記で作成した Cloud Functions `startInstancePubSub` に送信するデータを指定。
        - 今回の設定では、`{"zone":"自動起動したいインスタンスのゾーン", "instance":"自動起動したいインスタンスのインスタンス名、またはインスタンスID", "label":"startup=daily"}` のフォーマットで指定します。例えば、上記画面の例では、ゾーン（us-central1-c）にあるインスタンス（wuton-tryon2）を自動起動するためのペイロードになっています。
        - [Googleの公式サイト](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja) 上に説明では、`"label":"startup=daily"` の構文が含まれていませんが、最新のものでは、この構文も含める必要があるようです。

### 2.1 停止ジョブ作成
停止ジョブについても、起動ジョブのときと同様の手順で作成します。

1. [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler?hl=ja) ページに移動して、「ジョブを作成」をクリックします。
    <img src="/attachment/5e3ce57ab4655300410883df" width="450">
1. ジョブの作成画面の以下の項目を設定します。
    <img src="/attachment/5e3cf5e1b4655300410883e8" width="400">
    - 名前 : shutdown-workday-instance
        - 画面上の名前欄には、「この名前は既に使用されています」との警告が出ていますが、これはすでにこのジョブ作成済みの環境で撮影したためであり、新規に作成する場合はこのような警告は出てきません。
    - 頻度 : ジョブの実行頻度を cron 形式で入力します。
        - 上記画面の例では、毎日午後 22:00 にインスタンスを停止する設定になっています。
    - タイムゾーン : 日本時間で指定したければ、「日本標準時（JST）」を指定します。
    - ターゲット : Pub/Sub
    - トピック : stop-instance-event
    - ペイロード : 上記で作成した Cloud Functions `stopInstancePubSub` に送信するデータを指定。

起動ジョブと停止ジョブが正常に作成されれば、Cloud Scheduler 上の画面に以下のような２つのジョブ `startup-workday-instance`, `shutdown-workday-instance` が作成されています。
作成済みのジョブを編集したい場合は、ジョブを起動状態（再開ボタンクリックで起動）で編集ボタンをクリックしてくだい。停止状態では編集できないようです。

<img src="/attachment/5e3cf6d3b4655300410883e9" width="650">
    
## 3. 作成した関数とジョブの動作テスト
Cloud Scheduler の画面上で、「今すぐ実行」ボタンをクリックすることで、ジョブで設定した頻度の値に関わらず、各ジョブを即時実行する事ができます。
<img src="/attachment/5e3cf783b4655300410883ec" width="650">

今回の設定では、以下の動作が行われるはずです。
- ジョブ `startup-workday-instance` に対しての「今すぐ実行」ボタンをクリックすることで、ペイロードで指定したインスタンスが起動される
- ジョブ `shutdown-workday-instance` に対しての「今すぐ実行」ボタンをクリックすることで、ペイロードで指定したインスタンスが停止される。

うまく起動・停止できていない場合は、Cloud Functions か作成したジョブのペイロードの値の指定が誤っている可能性が高いです。

詳細なデバッグは、以下の手順で行えます。
- Cloud Functions の画面上に移動し、作成した関数をクリック
- 以下の画面から、ログを表示ボタンクリック
    <img src="/attachment/5e3cf992b4655300410883f1" width="550">
- ログファイルのメッセージを確認。
    <img src="/attachment/5e3cfac8b4655300410883f2" width="550">
    - ペイロードで指定したデータを、Cloud Functions が正しく認識していれば、「... finished with status: 'ok'」というメッセージが表示されます。
    - ペイロードで指定した json フォーマットに誤りがある場合は、「SyntaxError: Unexpected token “ in JSON at position ...」や「TypeError: First argument must be a string, Buffer, ArrayBuffer, Array, or array-like object. at Function.Buffer.from xxx」のメッセージが表示され、「... finished with status: 'error'」のメッセージが表示されます。


## 参考URL
- [Cloud Scheduler を使用した Compute インスタンスのスケジュール設定](https://cloud.google.com/scheduler/docs/start-and-stop-compute-engine-instances-on-a-schedule?hl=ja)