#-------------------------------
# プロバイダー設定
#-------------------------------
provider "aws" {
    profile = "Yagami360"
    region = "us-west-2"
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.eks.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.eks.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.eks.token
}

#-------------------------------
# 実行する Terraform 環境情報
#-------------------------------
terraform {
  required_version = "~> 1.0.8"

  # バックエンドを S3 にする
  backend "s3" {
    bucket = "terraform-tf-states-bucket"
    key = "aws/eks/terraform.tfstate"
  }

  # 実行するプロバイダー
  required_providers {
    aws       = {
      source  = "hashicorp/aws"
      version = "~> 3.71.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.5.0"
    }
  }
}

#-------------------------------
# IAM
#-------------------------------

#-------------------------------
# VPC
#-------------------------------

#-------------------------------
# EKS クラスター
#-------------------------------


#-------------------------------
# ノードプール
#-------------------------------
