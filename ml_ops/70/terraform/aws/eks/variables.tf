variable "profile" {
  default = "Yagami360"
}

variable "region" {
  default = "us-west-2"
}

variable "zone" {
  default = "us-west-2a"
}

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

# EC2 インスタンスで使用するキー名 / resource "aws_launch_configuration" で使用
variable "key_name" {
  default = "KEY"
}

# ローカル変数
locals {
  cluster_name    = "terraform-eks-cluster"   # variable で定義すると aleady exsist エラーになるケースがある？ので、local で定義
  cluster_version = "1.10"                    # variable で定義すると aleady exsist エラーになるケースがある？ので、local で定義
}
