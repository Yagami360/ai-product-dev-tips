#!/bin/sh
set -eu

IN_IMAGE_FILE="in_image/1.jpg"
IN_AUDIO_FILE="in_audio/1.mp3"
OUT_VIDEO_FILE="out_video/1.mp4"
FPS=10

mkdir -p `dirname ${OUT_VIDEO_FILE}`

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

# ffmpeg コマンドを用いて mp3 ファイルと画像ファイルから mp4 ファイルを作成する
ffmpeg -y -loop 1 -i ${IN_IMAGE_FILE} -i ${IN_AUDIO_FILE} -vcodec libx264 -acodec aac -ab 160k -ac 2 -ar 48000 -pix_fmt yuv420p -shortest ${OUT_VIDEO_FILE}

<<COMMENTOUT
ffmpeg \
	-i ${IN_IMAGE_FILE} -i ${IN_AUDIO_FILE} \
	-map 0:v -map 1:a \
	-loop 1 \
	-framerate 1 -r ${FPS} \
	-vf "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p" \
	-movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \
	${OUT_VIDEO_FILE}
COMMENTOUT
