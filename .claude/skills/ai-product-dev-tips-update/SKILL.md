---
name: ai-product-dev-tips-update
description: >-
  Update an EXISTING Tip in the ai-product-dev-tips repository — edit its README, add or fix code,
  refresh outdated information, fix mistakes — while keeping the repo's format conventions and
  syncing the root README link. Use this whenever the user wants to update, edit, fix, revise,
  refresh, correct, or complete an existing Tip in this repo — e.g.
  "nlp_processing/29 の README を更新して", "〇〇の Tip を最新仕様に直して",
  "image_processing/11 の説明を修正して", "あの Tip のリンク切れを直して", "この Tip を完成版にして".
  It locates the target Tip, studies the current format conventions (shared with the
  ai-product-dev-tips-create skill), applies consistent edits, verifies the content with web
  research (no fabrication), and syncs the root README link (title text / [In-progress]).
  This is for UPDATING existing Tips, not creating new ones — to add a brand-new Tip use the
  ai-product-dev-tips-create skill instead. Trigger this even if the user doesn't say "skill".
---

# 既存 Tip 更新スキル（ai-product-dev-tips）

このスキルは、ai-product-dev-tips リポジトリの**既存の Tip を更新**するためのものです。
新規 Tip の作成は行いません（それは姉妹スキル `ai-product-dev-tips-create` の役割です）。

更新の目的は、既存 Tip の README やコードを、内容の追記・修正・最新化・誤り訂正などで改善しつつ、リポジトリ全体の一貫性を保つことです。
書式・コード・検証の規約は `ai-product-dev-tips-create` と共通なので、その参照ファイルを流用します。

- 書式の規約: `.claude/skills/ai-product-dev-tips-create/references/readme-format.md`
- コード雛形の規約: `.claude/skills/ai-product-dev-tips-create/references/code-scaffold.md`

以下のステップを順番に実行します。

## ステップ1 — 更新対象の Tip を特定する

1. ユーザーの指示から、更新対象の Tip を特定する。
   `<category>/<番号>`（例: `nlp_processing/29`）が明示されていればそれを使う。
   タイトルやトピックだけ示された場合は、ルート `README.md` のリンクや各 Tip の見出しを検索して対象ディレクトリを特定する（例: `grep -rl "<キーワード>" */*/README.md`）。

2. 特定できない/複数候補がある場合は、候補を提示してユーザーに確認する。
   既存 Tip を取り違えて更新するのは避ける。

3. 対象ディレクトリと、その `README.md`（およびコードファイル）のフルパスを把握する。

## ステップ2 — 変更内容を把握する

1. ユーザーが何を変えたいのかを明確にする。
   追記・修正・最新化・誤り訂正・リンク修正・未完成の完成化（`[In-progress]` を外す）など、変更の種類を見極める。
   曖昧なら、どこをどう変えたいかを簡潔に確認する。

2. 既存の `README.md`（とコード）を**最後まで読む**。
   現状の構成・記述・主張を正しく理解してから手を入れる。
   既にある正しい記述や、ユーザーが意図して書いた内容を壊さないようにする。

## ステップ3 — 現状と最新フォーマットを調べる

更新後も、その Tip が「リポジトリの他の Tip と同じ作者が書いたように」見えるように、現在の慣習を確認する。
`ai-product-dev-tips-create` のステップ3と同じ要領で調べる。

1. `README_format.md` を読んで基本の発想を把握する（緩い骨子。字義どおりには従わない）。

2. **最新コミットの README フォーマットを優先的に確認する**。
   `git log -20 --name-only --pretty=format: -- '*/README.md' | grep README | sort -u` などで最近変更された Tip を特定し、現在の好ましい書き方（見出し構成・図の使い方・記述粒度）を掴む。

3. 同じカテゴリを中心に、他カテゴリも含めて既存 README を数本読み、書式の最新傾向に合わせる。
   ただし更新では、対象 Tip の既存スタイルを尊重し、必要な範囲の変更に留める（全面書き換えを目的にしない）。

## ステップ4 — README とコードを更新する

`.claude/skills/ai-product-dev-tips-create/references/readme-format.md` の規約に従って編集する。
更新時の要点は次の通り。

- 必要な箇所のみを変更し、関係ない部分は触らない。
  既存の構成を尊重しつつ、追記・修正・最新化を行う。
- 図表で視覚的にわかりやすくする。
  アーキテクチャ／フロー図は Mermaid 図を優先する（画像アップロード不要）。
  図には構造・グルーピング・フローの情報を持たせる。
  実スクリーンショットが必要なときだけ `<img ... src="https://github.com/user-attachments/assets/..." />` を使い、画像はアップロードできないので `<!-- TODO: 画像を貼り付け -->` のプレースホルダを残し、その旨をユーザーに伝える。
- 使い方／手順は、内部実装ではなく「外部から見た動かすための手順」を番号付きリストで書く（各項目 `1.` 始まり）。
  手順は具体的に書く。
  ただし正確なコマンド・識別子・パラメータ値が不確実な場合は、推測でもっともらしい値を捏造しない（`<!-- TODO: 要確認 -->` を残すか、ユーザーに確認する）。
- 同梱コードファイルは相対リンクで参照する（例: ``[`run.py`](run.py)``）。
- 参考 URL は `## 参考サイト` に置き、現行の公式 URL かユーザー提供のものを使う。
  古い／存在しない可能性のある URL を推測で書かない。

正確性の原則として、書く事実・コマンド・URL・バージョンはできる限り検証して書き、「それらしさ」より「正しさ」を優先する。
README は周囲の Tip に合わせて日本語で書く。

## ステップ5 — コードを追加・修正する（必要な場合）

更新でコードの追加・修正が必要な場合は、`.claude/skills/ai-product-dev-tips-create/references/code-scaffold.md` の規約に従う。
既存のコードがある場合は、そのスタイル（argparse の使い方、依存の固定方法、`*_cpu.sh`/`*_gpu.sh` や Dockerfile の有無など）に合わせる。
不要なコードは足さない。

## ステップ6 — 更新後の内容を検証する（過不足・矛盾・虚偽の確認）

更新したら、リンク同期・コミットの前に、内容を必ず自己検証する。
推測のまま確定させず、Web 調査で裏取りする。
`ai-product-dev-tips-create` のステップ6と同じ要領で行う。

- 過不足: 更新後の Tip に必要な前提・手順・説明が欠けていないか。逆に冗長・不要な記述が混ざっていないか。
- 矛盾: 記述同士で食い違いがないか。
  特に、更新で変えた箇所と、変えていない既存記述との間に矛盾が生じていないか。
  README の説明と同梱コード（実際の引数・関数名・デフォルト値・挙動）が一致しているか。
- 虚偽・不正確: 事実・コマンド名・API・オプション・URL・バージョンに誤りがないか。

検証の方法。

- 自分の知識だけで判断しない。
  間違えやすい／古くなりやすい点（コマンド名・API・公式 URL・最新仕様など）は、`/deep-research` や `WebFetch` / `WebSearch` で実際に確認する。
- URL は実際に開いて、生存とページ内容（リダイレクト先が変わっていないか等）を確認する。
- コード付き Tip では、README に書いた使い方とコードの実体を突き合わせる。

コードを追加・修正した場合は、`/code-review`（組み込み。手元の差分をレビュー）を実行し、バグや明らかな問題がないか確認する。
README のみの更新では `/code-review` の効果は限定的なので必須ではない。

見つかった問題は修正する。
確認できない事項は断定せず `<!-- TODO: 要確認 -->` を残すか、ユーザーに確認する。
この検証を、リンク同期・コミットの前のゲートとして必ず行う。

## ステップ7 — ルート `README.md` のリンクを同期する

更新内容に応じて、ルート `README.md` のリンクを既存のまま正しく保つ。

- Tip のタイトル（H1）を変更した場合は、ルート README の該当リンクの**テキストも同じタイトルに更新**する。
  リンク先 URL（`tree/master/<category>/<番号>`）は変えない。
- 未完成だった Tip を完成させた場合は、リンクテキスト先頭の `[In-progress]` を**外す**。
  逆に未完成のままなら `[In-progress]` を保持する。
  `[In-progress]` はリンクの角括弧の中（リンクテキストの先頭）にある（`- [[In-progress] <タイトル>](URL)`）。
- 番号・カテゴリ・リンクの掲載位置は**変えない**（移動・並べ替えはしない）。
- タイトルも In-progress も変わらない更新（本文・コードのみの修正）なら、ルート README は変更不要。

## ステップ8 — 報告する

ユーザーに簡潔に伝える。

- 更新した Tip の `README.md`（およびコード）のフルパス（絶対パス）。
- 何をどう変更したかの要約（必要なら `git --no-pager diff` の要点）。
- ルート README のリンクを同期したか（タイトル変更・`[In-progress]` の付け外し）、しなかったか。
- 残した `TODO`（画像アップロード、要確認の値・URL など）。

## コミット／反映について

既存 Tip の更新も、デフォルトで `master` ブランチへ直接コミット・push してよい（別ブランチ・PR は不要）。
ただしユーザーから「別ブランチで」「PR を作って」と依頼があればそれに従う。
コミット・push を行うのはユーザーがそれを望むときだけにし、勝手に push しない。

## やってはいけないこと

- 対象 Tip の**番号変更・カテゴリ移動・別 Tip 化**をしない。
  あくまで既存 Tip の中身の更新に留める。
- 目的に対して過剰な**全面書き換え**をしない。
  必要な範囲の変更に留め、既存の正しい記述やユーザーが意図した内容を壊さない。
- 新規 Tip を作らない（それは `ai-product-dev-tips-create` の役割）。
- URL や事実を推測で捏造しない。
  確認できないものはプレースホルダを残すかユーザーに確認する。
