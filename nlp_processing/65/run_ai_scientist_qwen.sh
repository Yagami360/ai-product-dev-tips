#!/bin/sh
# AI Scientist-v2 を「ローカルの Qwen（Ollama）」だけで動かすラッパースクリプト（API コスト $0）。
#
# 事前準備:
#   1. AI-Scientist-v2 を clone し、conda 環境を作成・有効化しておく:
#        git clone https://github.com/SakanaAI/AI-Scientist-v2.git
#        cd AI-Scientist-v2
#        conda create -n ai_scientist python=3.11 && conda activate ai_scientist
#        conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
#        conda install anaconda::poppler && conda install conda-forge::chktex
#        pip install -r requirements.txt
#   2. この Tip の以下 3 ファイルを AI-Scientist-v2 リポジトリ直下にコピーする:
#        my_research_topic.md  bfts_config_qwen.yaml  run_ai_scientist_qwen.sh
#   3. 本スクリプトを AI-Scientist-v2 リポジトリ直下で実行する（サンドボックス内推奨）:
#        sh run_ai_scientist_qwen.sh
#
# 注意: LLM が生成したコードを実行するため、必ず Docker 等の隔離環境・ネットワーク制限下で動かすこと。
set -eux

# ===== 設定 =====
TEXT_MODEL="ollama/qwen3:32b"          # コード生成・執筆・査読・引用など（軽く試すなら ollama/qwen3:8b）
VLM_MODEL="ollama/qwen2.5vl:32b"       # 図の視覚評価（VLM）。bfts_config_qwen.yaml 側でも指定
IDEA_MD="my_research_topic.md"         # ideation の入力トピック
IDEA_JSON="ai_scientist/ideas/my_research_topic.json"  # ideation の出力（experiment の入力）

# llm.py が参照する Ollama 用 API キー（ダミー値で可）
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

# ===== 0. Ollama モデルの取得（未取得ならダウンロード）=====
ollama pull "$(echo "${TEXT_MODEL}" | sed 's#^ollama/##')"
ollama pull "$(echo "${VLM_MODEL}"  | sed 's#^ollama/##')"

# ===== 1. Qwen 版の BFTS 設定を反映（launch は bfts_config.yaml 固定パスを読む）=====
cp bfts_config_qwen.yaml bfts_config.yaml

# ===== 2. Ideation（アイデア生成）=====
cp "${IDEA_MD}" ai_scientist/ideas/my_research_topic.md
python ai_scientist/perform_ideation_temp_free.py \
  --workshop-file "ai_scientist/ideas/my_research_topic.md" \
  --model "${TEXT_MODEL}" \
  --max-num-generations 20 \
  --num-reflections 5

# ===== 3. Experiment（Agentic Tree Search）＋ Writeup ＋ Review =====
# code / feedback / vlm_feedback / report のモデルは bfts_config.yaml 側で Qwen を指定済み。
# CLI 側の各 --model_* もすべて Qwen にする（--model_writeup_small も指定しないと既定で GPT-4o を呼ぶ点に注意）。
python launch_scientist_bfts.py \
  --load_ideas "${IDEA_JSON}" \
  --load_code \
  --add_dataset_ref \
  --model_writeup "${TEXT_MODEL}" \
  --model_writeup_small "${TEXT_MODEL}" \
  --model_citation "${TEXT_MODEL}" \
  --model_review "${TEXT_MODEL}" \
  --model_agg_plots "${TEXT_MODEL}" \
  --num_cite_rounds 20

echo "done. 出力は experiments/<timestamp>/ 以下（unified_tree_viz.html と論文 PDF）を確認"
