import os
import argparse
import time, datetime
from google.cloud import pubsub_v1

def callback(message):
    """
    トピックにメッセージが届いたときに呼び出されるコールバック関数
    """
    now = datetime.datetime.now()
    print( "msg = \"" + message.data.decode("utf-8") + "\"" +  "  [" + now.isoformat(" ") + "]")

    # ACK メッセージを送信（受信メッセージの処理が完全に完了したことを通知）
    message.ack()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
    parser.add_argument("--sub_name", type=str, default="sub-sample", help="サブスクリプション名")
    parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # subscriber のインスタンス作成
    subscriber = pubsub_v1.subscriber.Client.from_service_account_file(args.credentials_file_path)
    subpath = subscriber.subscription_path(args.project_id, args.sub_name)
    flow_control = pubsub_v1.types.FlowControl(max_messages=2)

    # トピックのメッセージを subscribe (pop) する
    subscriber.subscribe(subpath, callback=callback, flow_control = flow_control)
    input()
