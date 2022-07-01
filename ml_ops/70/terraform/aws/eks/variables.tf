variable "profile" {
  default = "Yagami360"
}

variable "region" {
  default = "us-west-2"
}

# data {...} ブロックを使用することで、Terraform 外部で定義されたデータを取得して、tf ファイル内で利用することができる
# data "aws_availability_zones" {...} を使用すると、プロバイダ provider "aws" で設定されたリージョン内のAWSアカウントでアクセス可能な AWS Availability Zones のリストにアクセスすることを可能に
data "aws_availability_zones" "available" {
}

#variable "zone" {
#  default = "us-west-2a"
#}

variable "num_subnets" {
  default = 2
}

variable "vpc_cidr_block" {
  default = "10.0.0.0/16"
}

#variable "cluster_name" {
#  default = "terraform-eks-cluster"
#}

#variable "cluster_version" {
#  default = "1.10"
#}

variable "instance_type" {
  default = "t2.small"
}

# EC2 インスタンスで使用するキー名（`.ssh/**.pem` の ** の部分）/ resource "aws_launch_configuration" で使用
variable "key_name" {
  default = "key"
}

# ローカル変数
locals {
  cluster_name    = "terraform-eks-cluster"   # variable で定義すると aleady exsist エラーになるケースがある？ので、local で定義
  #cluster_version = "1.10"                   
  cluster_version = "1.20"                    # "1.10" だと `unsupported Kubernetes version` エラーができるので、1.20 を使用
}
