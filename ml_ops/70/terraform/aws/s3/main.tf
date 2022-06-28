#-------------------------------
# プロバイダー設定
#-------------------------------
provider "aws" {
    #version = "~> 2.0"
    profile = "${var.profile}"
    region = "${var.region}"
}

#-------------------------------
# 実行する Terraform 環境情報
#-------------------------------
terraform {
  # terraform のバージョン
  #required_version = "~> 1.2.0"

  # 実行するプロバイダー
#  required_providers {
#    aws       = {
#      source  = "hashicorp/aws"
#      version = "~> 3.71.0"
#    }
#  }
}

#-------------------------------
# Amazon S3 パケット
#-------------------------------
resource "aws_s3_bucket" "terraform_tf_states_bucket" {
    bucket = "${var.bucket_name}"
    acl = "private"     # S3 上の ACL 指定 ※現バージョンでは private しか指定できない
}
