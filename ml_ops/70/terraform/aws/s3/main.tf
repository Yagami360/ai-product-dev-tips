#-------------------------------
# プロバイダー設定
#-------------------------------
provider "aws" {
    #version = "~> 2.0"
    profile = "Yagami360"
    region = "us-west-2"
}

#-------------------------------
# Amazon S3 パケット
#-------------------------------
resource "aws_s3_bucket" "terraform_tf_states_bucket" {
    bucket = "terraform-tf-states-bucket"
    acl = "private"     # S3 上の ACL 指定 ※現バージョンでは private しか指定できない
}
