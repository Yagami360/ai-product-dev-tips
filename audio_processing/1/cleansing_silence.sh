#!/bin/sh
set -eu

IN_AUDIO_FILE="in_audio/001-sibutomo.mp3"
OUT_AUDIO_FILE="out_video/001-sibutomo.mp3"
MIN_SILENCE_LEN=1500
SILENCE_THRESH=-30
KEEP_SILENCE=500
mkdir -p `dirname ${OUT_AUDIO_FILE}`

# OS 判定
if [ "$(uname)" = 'Darwin' ]; then
	OS='Mac'
	echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
	OS='Linux'
	echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then
	OS='Cygwin'
	echo "Your platform is Cygwin."  
else
	echo "Your platform ($(uname -a)) is not supported."
	exit 1
fi

# ffmpeg をインストール
ffmpeg -version &> /dev/null
if [ $? -ne 0 ] ; then
	if [ ${OS} = "Mac" ] ; then
		#git -C /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core fetch --unshallow
		#brew style --fix
		brew install ffmpeg
	elif [ ${OS} = "Linux" ] ; then
		sudo apt install ffmpeg
	fi
fi

# pydub をインストール
pip install pydub

# 音声ファイルの無音部分をクレンジングする
python cleansing_silence.py \
	--in_audio_file ${IN_AUDIO_FILE} \
	--out_audio_file ${OUT_AUDIO_FILE} \
	--min_silence_len ${MIN_SILENCE_LEN} \
	--silence_thresh ${SILENCE_THRESH} \
	--keep_silence ${KEEP_SILENCE}
