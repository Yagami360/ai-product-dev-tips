# 【GCP】サーバー起動後に自動的に実行するスクリプトを設定する。
本記事は、GCPインスタンス起動時に指定したスクリプトを自動的に実行する方法についての記事です。

この方法を使用することにより、例えば、GCPインスタンス起動時に指定の docker 環境や WebAPI などを自動的に実行し、利用可能な状態にするといった活用が可能となります。
又、本手法と別記事「[【GCP】Cloud Scheduler 機能を用いて、サーバーを一定の時間間隔で起動・停止する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/4)」 で紹介している方法と組み合わせることで、「GCPインスタンスを指定した時間スケジュールで起動・停止させつつ、起動時には WebAPI などを実行可能な状態にしておく」といった活用が可能となります。

## 1. 起動時に自動的に実行するスクリプトを作成する
シェルスクリプト（.sh）で、インスタンス起動時に自動的に実行させた独自のスクリプトを作成してくだい。
※ Pythonスクリプト（.py）でも以下で紹介する同様の方法で自動実行可能となるかは、確認していません。

## 2. Google Storage に、作成した起動スクリプトをアップロードする。
<img src="/attachment/5e3d054cb465530041088403" width="650">

1. Google Storage ページに移動し、作成した起動スクリプトをアップロードします。
   - 上記画面上の例では、run_all.sh がこれに該当しています。
1. アップロードしたスクリプトの公開アクセスを公開に設定します。
   - 公開に設定するためには、アップロードした起動スクリプトをクリックした後に表示される以下の画面から、「権限を編集」ボタンをクリックし、ユーザーに「allUsers」を追加して保存すればよいです。
    <img src="/attachment/5e3d041cb465530041088402" width="500">
1. 公開アクセスのアイコンを右クリックし、アップロードした起動スクリプトのリンクURLをコピーします。
    - この画面上の例では、https://storage.googleapis.com/api-server/run_all.sh がコピーするべきURL になっています

## 3. 起動スクリプトのリンクを、インスタンスのメタデータとして設定する。
インスタンスのカスタムメタデータに起動スクリプトのリンクを設定することで、GCPインスタンス起動時にそのスクリプトを自動的に実行することができます。

1. インスタンスの編集画面から、カスタムメタデータの「項目を追加」ボタンをクリックします。
2. キーに「startup-script-url」を設定し、値に「先程コピーした起動スクリプトのURL」を設定します。。
    <img src="/attachment/5e3d0776b465530041088404" width="500">
1. 全ての設定完了後、インスタンスを保存します。

以上の設定が全て完了した後に、インスタンスを起動することで、アップロードした起動スクリプトが自動的に実行されるはずです。