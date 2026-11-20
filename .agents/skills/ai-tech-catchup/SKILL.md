---
name: ai-tech-catchup
description: '最新AI技術動向のレポート（最新 / 週次 / 月次 / 特定トピック別）を Web 検索・ページ取得・GitHub/Hugging Face MCP で調査して生成し、Yagami360/ai-product-dev-tips リポジトリの GitHub Issue として投稿するスキル。ユーザーが「AI技術のキャッチアップ」「最新AIニュースまとめ」「週次/月次のAI動向レポート」「〇〇（例: AI Agent, RAG, VLM, Physical AI, Claude Code）についての技術調査レポート」「AI Tech Catchup レポートを作って」などを求めたとき、たとえ "skill" や "Issue" という単語が無くても必ずこのスキルを使うこと。直近のAI業界の最新情報を調べてまとめてほしい・GitHub Issue 化してほしいという依頼全般で発動する。AI とは無関係な一般的な技術調査や、このリポジトリへの Tip 追加（ai-product-dev-tips-create スキルの領分）には使わない。'
---

# AI Tech Catchup

最新の AI 技術動向を調査し、構造化されたレポートを GitHub Issue として投稿するスキル。Codex がそのまま調査エージェントとして動き、Web 検索 / ページ取得 と（利用可能なら）GitHub・Hugging Face の MCP サーバーで情報を集める。

レポートの投稿先は **`Yagami360/ai-product-dev-tips`** リポジトリの Issue（このスキルが置かれているリポジトリ）。

## レポートの 4 種別

| 種別 | いつ使うか | デフォルト件数 |
|------|-----------|---------------|
| **最新 (latest)** | 「今のAI動向」「最新ニュースまとめ」など、期間を区切らない直近の総まとめ | 20 |
| **週次 (weekly)** | 「先週の」「週次の」AI動向。前日までの過去7日間 | 10 |
| **月次 (monthly)** | 「先月の」「月次の」AI動向。前日までの過去30日間 | 20 |
| **トピック別 (topic)** | 特定テーマ（例: AI Agent, RAG, VLM, Physical AI, Claude Code）の深掘り | 20 |

**このスキルは Codex のスケジュールからも無人で実行できる。** 種別が不明なときは最新 (latest) をデフォルトとし、与えられた情報で調査 → レポート生成 → 明示的に依頼された GitHub Issue 投稿まで自動で進める。

## 手順

### 1. 種別と引数を決める

- 依頼（スケジュールのプロンプト）から種別を判定する。トピック別ならトピック名を抽出する（不明なら最も妥当なものを採る。確認はしない）。
- 件数はユーザー指定があれば優先、無ければ上表のデフォルト。
- 週次・月次は調査期間を計算する。**前日**を終点に固定（実行日当日は含めない）。計算式は `references/report-formats.md` の「期間の計算」に従う。今日の日付はシステムのコンテキスト（現在日付）を使う。

### 2. 調査の材料を読み込む

- `references/sources.md` — 調査対象の AI 技術キーワード・優先情報源 URL・MCP 活用ガイド。
- `references/report-formats.md` — 選んだ種別の出力フォーマット（見出し構成）と Issue 本文テンプレート。

### 3. 調査する

`references/sources.md` の情報源を**優先的に**当たりつつ、必要に応じて関連 URL も調べる。リアルタイム性が最重要なので、推測や古い知識で埋めず、実際に検索・取得した情報を使う。

調査は **「Web 調査」と「MCP サーバーでの補強」を組み合わせて**行う。
Web 調査は、軽い場合は通常の検索（方法 A）、裏取り重視なら Codex の深掘り Web 調査（方法 B）を使う。
**Codex の深掘り Web 調査 を使う場合でも、使える MCP サーバー（GitHub / Hugging Face / arXiv）は併用して OSS・モデル・論文動向を補強する**（MCP は方法 A・B のどちらとも組み合わせる）。

#### Web 調査 — 方法 A: 通常の Web 検索（デフォルト）

軽量・高速。各セクションを埋める材料が揃えばよい場合に使う。

- **Web 検索 / ページ取得**: 優先情報源（企業公式ブログ、技術ニュース、arXiv、GitHub Trending、Hugging Face、SNS など）から、新製品・新機能・研究論文・投資/M&A・OSS 動向を収集する。**並列で複数の検索を走らせる**と速い。
- あわせて、下記の **MCP サーバー（GitHub / Hugging Face / arXiv）も併用**して OSS・モデル・論文動向を補強する（方法 A でも MCP を使う）。

#### Web 調査 — 方法 B: Codex の Web 検索とページ取得で深掘り

より網羅的で**ファクトチェック済み**の調査が欲しいとき（ユーザーが「deep-research で」「しっかり裏取りして」「徹底的に調べて」等と言ったとき、またはトピック別レポートで深掘りしたいとき）に使う。Codex の深掘り Web 調査 では複数の Web 検索を並行し、ソースを取得し、主張を突き合わせて出典付きで統合する。

手順:

1. Codex の Web 検索とページ取得で、**レポート種別・期間・重点キーワードを織り込んだ具体的な調査**を行う。例:
   - 最新: 「2026年6月時点の最新AI技術動向を調査。LLM/AI Agent/VLM/Physical AI/AI Chips/OSS(GitHub・Hugging Face)/主要企業(OpenAI・Anthropic・Google・NVIDIA)の新発表・研究論文・投資M&A・市場動向を、出典URL付きで網羅的に。」
   - 週次/月次: 上記に「**調査期間 `2026-05-28 ~ 2026-06-03` に限定**」を追加。
   - トピック別: 「『AI Agent』に特化して、定義・最新動向・主要論文・OSS・市場規模・課題・展望を出典付きで深掘り。」
   - 必要なら `references/sources.md` のキーワード・優先情報源を依頼文に貼り込み、調査範囲を誘導する。
2. 検索で取得した一次情報を相互に検証し、出典付きの知見をまとめる。
3. その知見を**そのまま貼らず**、`references/report-formats.md` の該当種別の見出し構成に**並べ替えて**本文化する（ステップ 4）。

> Codex の深掘り Web 調査 は時間とトークンを多く使う。軽い最新まとめなら方法 A、裏取り重視の月次・トピック深掘りなら方法 B。**いずれの場合も下記の MCP サーバーを併用する。**

#### MCP サーバーで補強（方法 A・B のどちらでも併用する）

OSS・モデル・論文の動向は、上の Web 調査と**並行して**、使える MCP サーバーでも確認すると精度が上がる。
使えない環境では無理に呼び出さず、Codex の Web 検索 / ページ取得（`arxiv.org` 直接アクセスを含む）で代替する。

- **GitHub MCP サーバー**: 注目リポジトリの最新コミット/Issue/PR、Trending、リリースノート、主要 Organization の活動を確認。
- **Hugging Face MCP サーバー**: キーワード／トピック関連の最新モデル・データセット・Space・論文を検索し、人気度や差分を把握。
- **arXiv MCP サーバー**: `search_papers` でキーワード／トピック・期間・カテゴリ（cs.AI / cs.CL / cs.LG など）に絞って最新論文を検索し、必要に応じて `download_paper` / `read_paper` で内容まで踏み込む。論文動向の裏取りに使う。

どちらの方法でも、フォーマットの各セクションを埋めるのに十分な材料が集まったら次へ進む。情報が薄いセクションは無理に水増しせず、得られた事実ベースで簡潔に書く。

> **トークン量が多くなりがちな調査タスク**なので、独立した複数ソースの調査を並行して進めてよい。サブエージェントが使える環境では、種別やトピックに応じて調査を分担させると網羅性が上がる。

### 4. レポート本文を書く

`references/report-formats.md` の該当種別の見出し構成を**そのまま**使って本文を書く。**`report-formats.md` 冒頭の「共通ルール」（各項目を「太字の見出し ＋ 説明文」の二層で詳しく書く）に必ず従う**。要点:

- 各項目は**「太字の見出し ＋ 説明文」の二層**で書く。語句だけ・1 行だけの素っ気ない箇条書きにしない。重要ニュースは各項目 2〜4 文、トレンド/変化系は各項目 1〜2 文で、固有名詞・数値・背景・なぜ重要かを具体的に説明する。
- 各情報に**出典 URL** を必ず添える。日付・具体的な数値を入れる。
- 当年の最新情報を優先。トピック別はそのトピックに特化した実用的な内容にする。

### 5. Issue を投稿する

レポート本文ができたら、**投稿を明示的に依頼された場合は、追加確認なしで GitHub Issue を作成する**（Codex のスケジュールに投稿の指示が含まれている場合も同様）。

1. `references/report-formats.md` の「Issue 本文テンプレート」のヘッダ・フッタでレポート本文を囲み、一時ファイル（実行ごとに `mktemp` で作成し、処理後に削除）に書き出す。
   - 使用モデルにはこのセッションのモデル名を入れる。
   - **「調査方法」欄には、この調査で実際に使ったツールを正直に列挙する**（例: `Web 検索, ページ取得, Hugging Face MCP, arXiv MCP, Codex の深掘り Web 調査`）。使わなかったツールは書かない。MCP が使えず Web 検索のみだった場合はそう書く。
2. Codex の GitHub 接続ツール（`github_create_issue` とラベル付与ツール）、または認証済みの `gh` で投稿する。**基本のラベルは次の2種**。未作成なら作ってから付与する（冪等）。
   - 種別ラベル: `report` / `weekly-report` / `monthly-report` / `topic-report`
   - **使用モデル名のラベル**: このセッションのモデル名（例: `gpt-6.1-sol`）

   呼び出し元（Codex のスケジュールなど）が `codex-scheduled-task` ラベルの付与を指示している場合は、それも付ける。**スキル単独で実行した場合は付けない**（スケジュール経由ではないため）。`codex-scheduled-task` は共通ラベルとしてリポジトリ側に用意されている前提で、スキルからは作成しない。

   ```bash
   report_file="<作成した一時ファイルのパス>"
   MODEL="<このセッションのモデル名>"   # 例: gpt-6.1-sol

   # ラベルが無ければ作成（既にあればスキップ）
   gh label create weekly-report --repo Yagami360/ai-product-dev-tips --color 0e8a16 --description "AI Tech Catchup weekly report" 2>/dev/null || true
   gh label create "$MODEL" --repo Yagami360/ai-product-dev-tips --color 1d76db --description "Model used" 2>/dev/null || true

   # 本文はファイルに書き出してから --body-file で渡す（長文・改行・絵文字の安全な投稿のため）
   gh issue create \
     --repo Yagami360/ai-product-dev-tips \
     --title "📊 AI Tech Catchup Weekly Report - 2026年06月第1週" \
     --label weekly-report \
     --label "$MODEL" \
     --body-file "$report_file"
   # ↑ スケジュールから「codex-scheduled-task を付ける」指示がある場合のみ、--label codex-scheduled-task を追加する
   ```

3. 投稿後、作成された Issue の URL を報告する。

## メモ

- 本文は一時ファイル（実行ごとに `mktemp` で作成し、処理後に削除）に書き出してから `--body-file` で渡すと、長文・絵文字・コードブロックを安全に投稿できる。`--body` に直接巨大な文字列を渡すのは避ける。
- `--no-issue` 相当（投稿せず本文だけ欲しい）とユーザーが言った場合は、本文を提示するだけで終える。
- このスキルは AI 技術動向の調査・レポート専用。AI と無関係な調査や、このリポジトリへの Tip 追加（`ai-product-dev-tips-create`）・既存 Tip の更新（`ai-product-dev-tips-update`）とは役割が異なる。
