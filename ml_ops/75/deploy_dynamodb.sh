#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

TABLE_NAME="sample-table"

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
# Amazon DynamoDB リソース削除
#=============================
sh delete_dynamodb.sh

#=============================
# Amazon DynamoDB リソース作成
#=============================
mkdir -p log

# テーブルを作成する（コマンド実行後、コンソール出力画面で待機状態になるので ``> log/${TABLE_NAME}.json`` でコンソール出力を外部出力する）
aws dynamodb create-table --table-name ${TABLE_NAME} \
    --attribute-definitions \
    	AttributeName=id,AttributeType=N \
	  	AttributeName=name,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
        AttributeName=name,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=10,WriteCapacityUnits=10 \
    --table-class STANDARD > log/${TABLE_NAME}.json

sleep 5

# テーブル一覧を確認
aws dynamodb list-tables

# テーブル詳細を確認
#aws dynamodb describe-table --table-name ${TABLE_NAME}

# データベースのテーブルを更新する
aws dynamodb update-table --table-name ${TABLE_NAME} \
	--provisioned-throughput '{"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}' > log/${TABLE_NAME}.json

# テーブルにアイテムを追加する
aws dynamodb put-item --table-name ${TABLE_NAME} \
	--item '{ "id": { "N": "1" }, "name": { "S": "yagami" } }'

# テーブルのアイテムを取得する
aws dynamodb get-item --table-name ${TABLE_NAME} \
	--key '{ "id": { "N": "1" }, "name": { "S": "yagami" } }'
