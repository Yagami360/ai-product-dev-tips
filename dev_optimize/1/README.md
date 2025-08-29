# Claude Code GitHub Actions を使用して PR レビューを自動化する

## 方法

1. Claude の API キーを作成する

    <img width="500" height="405" alt="Image" src="https://github.com/user-attachments/assets/db479178-e777-4b29-b596-353bc876eb5c" />

2. 以下のリンクから **Claude GitHubアプリをインストール**してリポジトリに追加する

    https://github.com/apps/claude

    <img width="500" height="411" alt="Image" src="https://github.com/user-attachments/assets/ab03351a-dea1-45cc-b1af-9cb82cde3989" />

3. Claude API キーの環境変数 `ANTHROPIC_API_KEY` を各リポジトリの GitHub シークレットに追加する

    <img width="728" height="606" alt="Image" src="https://github.com/user-attachments/assets/baa344ee-a0cf-4377-9ffc-b95f6279f0d9" />

4. レポジトリに GitHubActions の定義ファイルを追加する

    https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml の GitHubAction 定義ファイルを参考に、Claude Code GitHub Actions を使用した GitHubActions ワークフローを作成し、レポジトリの [`.github/workflows/claude.yml`](../../.github/workflows/claude.yml) に配置する


5. [Option] CAUDE.md を追加して、

## ワークフロー設定

PR、Issueでのコメントベースでのレビューに特化したワークフローです。

**トリガー条件:**
- PR・Issueコメントで `@claude` と入力
- PRレビューコメントで `@claude` と入力

**用途:**
- 既存PRのコードレビュー
- Issue・PRでの質問対応
- コード改善提案

## 使い方

1. **既存のPRでレビューを受ける**
   ```
   @claude このコードをレビューしてください
   ```

2. **Issueで質問する**
   ```
   @claude この実装方法について教えてください
   ```

## 参考サイト

- https://docs.anthropic.com/ja/docs/claude-code/github-actions
