#-------------------------------
# プロバイダー設定
#-------------------------------
provider "google" {
  project = "my-project2-303004"
  region  = "us-central1"
}

#-------------------------------
# 実行する Terraform 環境情報
#-------------------------------
terraform {
  # バックエンドを GCS にする（初回の GCS パケット未作成時はエラーになるのでコメントアウト）
#  backend "gcs" {
#    bucket = "terraform-tf-states-bucket"
#    prefix = "gcp/gcs"
#  }

  # プロバイダー情報
#  required_providers {
#    google = {
#      version = "~> 4.13.0"
#    }
#  }
}

#-------------------------------
# 各種 GCP サービス有効化
#-------------------------------
resource "google_project_service" "enable_iamcredentials" {
  service = "iamcredentials.googleapis.com"
}

resource "google_project_service" "enable_secretmanager" {
  service = "secretmanager.googleapis.com"
}

resource "google_project_service" "enable_cloudresourcemanager" {
  service = "cloudresourcemanager.googleapis.com"
}

#-------------------------------
# GCS パケット
#-------------------------------
# tfstate ファイルを保存する GCS パケット
# terraform apply で作成したインフラ情報は、*.tfstate ファイルに保存され、次回の terraform apply 実行時等で前回のインフラ状態との差分をみる際に利用されるが、
# tfstate ファイルをローカルに置いたままでは複数人で terraform を実行できなくなってしまうので、GCS に保存する
resource "google_storage_bucket" "terraform-tf-states" {
  name          = "terraform-tf-states-bucket"
  location      = "ASIA"
  versioning {
    enabled = true
  }
}
