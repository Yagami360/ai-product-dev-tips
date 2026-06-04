---
name: ai-tech-catchup
description: 最新AI技術動向のレポート（最新 / 週次 / 月次 / 特定トピック別）を Web 検索・WebFetch・GitHub/Hugging Face MCP で調査して生成し、Yagami360/ai-product-dev-tips リポジトリの GitHub Issue として投稿するスキル。ユーザーが「AI技術のキャッチアップ」「最新AIニュースまとめ」「週次/月次のAI動向レポート」「〇〇（例: AI Agent, RAG, VLM, Physical AI, Claude Code）についての技術調査レポート」「AI Tech Catchup レポートを作って」などを求めたとき、たとえ "skill" や "Issue" という単語が無くても必ずこのスキルを使うこと。直近のAI業界の最新情報を調べてまとめてほしい・GitHub Issue 化してほしいという依頼全般で発動する。AI とは無関係な一般的な技術調査や、このリポジトリへの Tip 追加（ai-product-dev-tips-create スキルの領分）には使わない。
---

# AI Tech Catchup

最新の AI 技術動向を調査し、構造化されたレポートを GitHub Issue として投稿するスキル。Claude Code がそのまま調査エージェントとして動き、WebSearch / WebFetch と（利用可能なら）GitHub・Hugging Face の MCP サーバーで情報を集める。

レポートの投稿先は **`Yagami360/ai-product-dev-tips`** リポジトリの Issue（このスキルが置かれているリポジトリ）。

## レポートの 4 種別

| 種別 | いつ使うか | デフォルト件数 |
|------|-----------|---------------|
| **最新 (latest)** | 「今のAI動向」「最新ニュースまとめ」など、期間を区切らない直近の総まとめ | 20 |
| **週次 (weekly)** | 「先週の」「週次の」AI動向。前日までの過去7日間 | 10 |
| **月次 (monthly)** | 「先月の」「月次の」AI動向。前日までの過去30日間 | 20 |
| **トピック別 (topic)** | 特定テーマ（例: AI Agent, RAG, VLM, Physical AI, Claude Code）の深掘り | 20 |

種別がはっきりしない場合は、何を作るか（種別・トピック名）を一言確認してから進める。

## 手順

### 1. 種別と引数を決める

- ユーザーの依頼から種別を判定する。トピック別ならトピック名を抽出する（曖昧なら確認）。
- 件数はユーザー指定があれば優先、無ければ上表のデフォルト。
- 週次・月次は調査期間を計算する。**前日**を終点に固定（実行日当日は含めない）。計算式は `references/report-formats.md` の「期間の計算」に従う。今日の日付はシステムのコンテキスト（currentDate）を使う。

### 2. 調査の材料を読み込む

- `references/sources.md` — 調査対象の AI 技術キーワード・優先情報源 URL・MCP 活用ガイド。
- `references/report-formats.md` — 選んだ種別の出力フォーマット（見出し構成）と Issue 本文テンプレート。

### 3. 調査する

`references/sources.md` の情報源を**優先的に**当たりつつ、必要に応じて関連 URL も調べる。リアルタイム性が最重要なので、推測や古い知識で埋めず、実際に検索・取得した情報を使う。

調査方法は 2 つある。ユーザーの希望や状況で選ぶ。**どちらの場合も、OSS・モデル動向は GitHub / Hugging Face MCP（使えれば）で補強する。**

#### 方法 A: 通常の Web 検索（デフォルト）

軽量・高速。各セクションを埋める材料が揃えばよい場合に使う。

- **WebSearch / WebFetch**: 優先情報源（企業公式ブログ、技術ニュース、arXiv、GitHub Trending、Hugging Face、SNS など）から、新製品・新機能・研究論文・投資/M&A・OSS 動向を収集する。**並列で複数の検索を走らせる**と速い。
- **GitHub MCP サーバー**（使える場合）: 注目リポジトリの最新コミット/Issue/PR、Trending、リリースノート、主要 Organization の活動を確認。
- **Hugging Face MCP サーバー**（使える場合）: キーワード／トピック関連の最新モデル・データセット・Space・論文を検索し、人気度や差分を把握。
- MCP サーバーが使えない環境なら無理に呼び出さず、Web 検索で代替する。

#### 方法 B: `/deep-research` コマンドで深掘り調査

より網羅的で**ファクトチェック済み**の調査が欲しいとき（ユーザーが「deep-research で」「しっかり裏取りして」「徹底的に調べて」等と言ったとき、またはトピック別レポートで深掘りしたいとき）に使う。`/deep-research` は Web 検索をファンアウトし、ソースを取得し、主張を敵対的に検証して出典付きで統合するハーネス。

手順:

1. `deep-research` スキルを呼び出す（Skill ツール、または会話で `/deep-research`）。`args` には、**レポート種別・期間・重点キーワードを織り込んだ具体的な調査依頼**を渡す。例:
   - 最新: 「2026年6月時点の最新AI技術動向を調査。LLM/AI Agent/VLM/Physical AI/AI Chips/OSS(GitHub・Hugging Face)/主要企業(OpenAI・Anthropic・Google・NVIDIA)の新発表・研究論文・投資M&A・市場動向を、出典URL付きで網羅的に。」
   - 週次/月次: 上記に「**調査期間 `2026-05-28 ~ 2026-06-03` に限定**」を追加。
   - トピック別: 「『AI Agent』に特化して、定義・最新動向・主要論文・OSS・市場規模・課題・展望を出典付きで深掘り。」
   - 必要なら `references/sources.md` のキーワード・優先情報源を依頼文に貼り込み、調査範囲を誘導する。
2. `/deep-research` が返した**検証済みの出典付き知見**を受け取る。
3. その知見を**そのまま貼らず**、`references/report-formats.md` の該当種別の見出し構成に**並べ替えて**本文化する（ステップ 4）。`/deep-research` が手薄なOSS/モデル情報は GitHub / Hugging Face MCP で補う。

> `/deep-research` は時間とトークンを多く使う。軽い最新まとめなら方法 A、裏取り重視の月次・トピック深掘りなら方法 B、と使い分ける。

どちらの方法でも、フォーマットの各セクションを埋めるのに十分な材料が集まったら次へ進む。情報が薄いセクションは無理に水増しせず、得られた事実ベースで簡潔に書く。

> **トークン量が多くなりがちな調査タスク**なので、独立した複数ソースの調査を並行して進めてよい。サブエージェントが使える環境では、種別やトピックに応じて調査を分担させると網羅性が上がる。

### 4. レポート本文を書く

`references/report-formats.md` の該当種別の見出し構成を**そのまま**使って本文を書く。共通ルール:

- 各項目は**簡潔な箇条書き**。冗長な説明は避ける。
- 各情報に**出典 URL** を必ず添える。日付・具体的な数値を入れる。
- 当年の最新情報を優先。トピック別はそのトピックに特化した実用的な内容にする。

### 5. プレビュー → 確認 → Issue 投稿

いきなり Issue を作らない。GitHub Issue の作成は外部に公開される取り消しにくい操作なので、**必ず先に本文をユーザーに提示して確認を取る**。

1. `references/report-formats.md` の「Issue 本文テンプレート」のヘッダ・フッタでレポート本文を囲む。使用モデルにはこのセッションのモデル名を入れる。
2. 完成した Issue タイトルと本文をチャットに提示し、「この内容で `Yagami360/ai-product-dev-tips` に Issue を作成してよいか」を確認する。
3. ユーザーが承認したら `gh` で投稿する。ラベル（`report` / `weekly-report` / `monthly-report` / `topic-report`）はこのリポジトリに未作成のことがあるので、無ければ作ってから付与する:

   ```bash
   # ラベルが無ければ作成（既にあればスキップ）
   gh label create weekly-report --color 0e8a16 --description "AI Tech Catchup weekly report" 2>/dev/null || true

   # 本文はファイルに書き出してから --body-file で渡す（長文・改行・絵文字の安全な投稿のため）
   gh issue create \
     --repo Yagami360/ai-product-dev-tips \
     --title "📊 AI Tech Catchup Weekly Report - 2026年06月第1週" \
     --label weekly-report \
     --body-file /tmp/ai-tech-catchup-report.md
   ```

4. 投稿後、作成された Issue の URL を報告する。

## メモ

- 本文は一時ファイル（例 `/tmp/ai-tech-catchup-report.md`）に書き出してから `--body-file` で渡すと、長文・絵文字・コードブロックを安全に投稿できる。`--body` に直接巨大な文字列を渡すのは避ける。
- `--no-issue` 相当（投稿せず本文だけ欲しい）とユーザーが言った場合は、本文を提示するだけで終える。
- このスキルは AI 技術動向の調査・レポート専用。AI と無関係な調査や、このリポジトリへの Tip 追加（`ai-product-dev-tips-create`）・既存 Tip の更新（`ai-product-dev-tips-update`）とは役割が異なる。
