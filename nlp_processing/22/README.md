# Dify を使用した LLM アプリケーションを Web アプリとして外部公開する

## 使用方法

1. 「[Dify の基本的な使い方（ワークフローを使用した LLM アプリケーションを作成する）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/20)」に従って、Dify を使用した LLM アプリケーションのワークフローを作成する

1. ワークフロー画面右上の「公開する」ボタンをクリックする<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/641d303b-47c5-4cae-b020-b0abd4b5fe7b"><br>

    「公開する」ボタンをクリック後、以下のような画面が表示される<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/f5edb340-f872-4800-bbf9-9617a1b096ef">

1. API として外部公開する<br>
    外部公開 API として使用する場合は、「APIリファレンスにアクセス」ボタンをクリックすると、以下のようなページが表示されるので curl コマンド等を使用して API 経由で LLM アプリケーションを利用する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/25e83dd6-f9f7-4b04-855a-fcb0f7ec6f0c">

    > API キーは、画面右上の「APIキー」ボタンから作成可能

    - ワークフローの実行（https://cloud.dify.ai/app/48859cb0-50c7-4e7e-ae47-dd1b3f3968f7/develop#Execute-Workflow）
        ```sh
        curl -X POST "https://api.dify.ai/v1/workflows/run" \
            --header "Authorization: Bearer ${API_KEY}" \
            --header "Content-Type: application/json" \
            --data-raw '{
                "inputs": {
                    "input_text": "Dify について教えて"
                },
                "response_mode": "streaming",
                "user": "user-1111111111111"
            }'
        ```
        - レスポンス例
            ```json
            ...
            data: {"event": "workflow_finished", "workflow_run_id": "f957cfa8-1855-470f-9947-dfe4379483e6", "task_id": "14b7df32-35f7-4894-b23f-8e7f182b96e0", "data": {"id": "f957cfa8-1855-470f-9947-dfe4379483e6", "workflow_id": "617aa409-35af-4284-a46a-767d1bbdd537", "sequence_number": 5, "status": "succeeded", "outputs": {"text": "ディフィーちゃんって、AIアニメキャラクターなんだよ！可愛らしい見た目と賢い頭脳を持っていて、いろんな質問に答えてくれるんだ。ディフィーちゃんとおしゃべりすると、楽しい時間が過ごせるよ！ディフィーちゃんはいつも元気いっぱいで、いろんな情報を教えてくれるよ！ぜひ一度、ディフィーちゃんとおしゃべりしてみてね！きっと楽しい体験ができるよ♪"}, "error": null, "elapsed_time": 1.9652793549466878, "total_tokens": 205, "total_steps": 3, "created_by": {"id": "c9500813-ff74-4a92-ab86-60072132d975", "user": "user-1111111111111"}, "created_at": 1720850792, "finished_at": 1720850794, "files": []}}
            data: {"event": "tts_message_end", "workflow_run_id": "f957cfa8-1855-470f-9947-dfe4379483e6", "task_id": "14b7df32-35f7-4894-b23f-8e7f182b96e0", "audio": ""}
            ```

        > 今回のワークフローの例では、入力変数として `input_text` にユーザーからの質問文を入力するようになっているので、`--data-raw` 引数の `inputs` フィールド内に `input_text` を設定して curl リクエストしている

1. 【オプション】公開したアプリを停止する場合<br>
    公開したアプリを停止させてい場合は、「概要」ページの「駆動中」->「無効」に切り替えれば、外部アクセスできなくなる<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/6307b107-6ff7-47e5-8fad-e9dea6cbc7a2">
