import os
import argparse
import time, datetime
from google.cloud import pubsub_v1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
    parser.add_argument("--topic_name", type=str, default="topic-sample", help="Pub/Sub のトピック名")
    parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
    parser.add_argument("--pub_times", type=str, default=10, help="送信回数")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # publisher のインスタンス作成
    publisher = pubsub_v1.publisher.Client.from_service_account_file(args.credentials_file_path)
    topic_path = publisher.topic_path(args.project_id, args.topic_name)

    # publish 処理
    for i in range(args.pub_times):
        # メッセージの設定
        data = u"Message from test publisher {}".format(i) + " | " + datetime.datetime.now().isoformat(" ")
        data = data.encode("utf-8")
        print("Publish: " + data.decode("utf-8", "ignore") )

        # トピックにメッセージを publish (push) する
        future = publisher.publish(topic_path, data=data)
        print("return ", future.result())
        time.sleep(0.25)
