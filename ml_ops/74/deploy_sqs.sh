#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

QUEUE_NAME="sample-queue"

#=============================
# OS判定
#=============================
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

#=============================
# AWS CLI のインストール
#=============================
aws --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    elif [ ${OS} = "Linux" ] ; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm awscliv2.zip
    fi
fi

echo "aws version : `aws --version`"

#=============================
# jq コマンドのインストール
#=============================
jq --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
		brew install jq
    elif [ ${OS} = "Linux" ] ; then
		sudo apt -y update
		sudo apt -y install jq
    fi
fi
echo "jq version : `jq --version`"

#=============================
# AWS デフォルト値の設定
#=============================
# アカウントID
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
cat ~/.aws/credentials

# AWS CLI のプロファイル
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${REGION}
cat ~/.aws/config

#=============================
# Amazon SQS リソース削除
#=============================
sh delete_sqs.sh

#=============================
# Amazon SQS リソース作成
#=============================
# キューを作成する
aws sqs create-queue --queue-name ${QUEUE_NAME}

# プロデューサー（送信側）でメッセージをキューに送信する
aws sqs send-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --message-body "hello world 1"
aws sqs send-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --message-body "hello world 2"
aws sqs send-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --message-body "hello world 3"

aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages

# コンシューマー（受信側）でキューからメッセージを受信する
mkdir -p log

aws sqs receive-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" > log/sqs_message_1.json
aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages
RECEIPT_HANDLE_1=$(jq -r '.Messages[].ReceiptHandle' log/sqs_message_1.json)
aws sqs delete-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --receipt-handle ${RECEIPT_HANDLE_1}
aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages

aws sqs receive-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" > log/sqs_message_2.json
RECEIPT_HANDLE_2=$(jq -r '.Messages[].ReceiptHandle' log/sqs_message_2.json)
aws sqs delete-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --receipt-handle ${RECEIPT_HANDLE_2}
aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages

aws sqs receive-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" > log/sqs_message_3.json
RECEIPT_HANDLE_3=$(jq -r '.Messages[].ReceiptHandle' log/sqs_message_3.json)
aws sqs delete-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --receipt-handle ${RECEIPT_HANDLE_3}
aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages