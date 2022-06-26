#-------------------------------
# プロバイダー設定
#-------------------------------
provider "google" {
  project = "my-project2-303004"
  region  = "us-central1"
  zone = "us-central1-b"
}

# Spot VM 使用時は必要
#provider "google-beta" {
#  project = "my-project2-303004"
#  region  = "us-central1"
#  zone    = "us-central1-c"
#}

#-------------------------------
# 実行する Terraform 環境情報
#-------------------------------
terraform {
  # terraform のバージョン
#  required_version = "~> 1.2.0"

  # バックエンドを GCS にする  
  backend "gcs" {
    bucket = "terraform-tf-states-bucket"
    prefix = "gcp/gke"
  }

  # プロバイダー情報
  required_providers {
    google = {
      version = "~> 4.13.0"   # Spot VM は、4.13.0 以上で使用可能
    }
  }
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
# GKE クラスタ
#-------------------------------
resource "google_container_cluster" "fast_api_terraform_cluster" {
  name     = "fast-api-terraform-cluster"
  location = "us-central1-b"    # 単一リージョンでのクラスタの場合は ZONE を指定。マルチゾーンクラスタの場合は REGION を指定
#  node_locations = [           # マルチゾーンクラスタの場合指定
#    "us-central1-a", "us-central1-b", "us-central1-f"
#  ]

  remove_default_node_pool = true   # デフォルトのノードプールを削除する
  initial_node_count       = 1

  network = "default"

  #min_master_version = "1.21.10-gke.2000"
  #node_version       = "1.12.6-gke.7"

#  master_auth {
#    username = ""      # Kubernetes master (mster ノード?) にアクセスするときの basic 認証に使用するユーザ名
#    password = ""      # Kubernetes master (mster ノード?) にアクセスするときの basic 認証に使用するパスワード

#    client_certificate_config {
#      issue_client_certificate = false
#    }
#  }
}

#-------------------------------
# ノードプール
#-------------------------------
resource "google_container_node_pool" "fast_api_cpu_pool" {
#  provider                  = google-beta   # SpotVM 使用時
  name       = "fast-api-cpu-pool"
  location   = "${google_container_cluster.fast_api_terraform_cluster.location}"
#  node_locations = [   # マルチゾーンクラスタの場合
#    "us-central1-a", "us-central1-b", "us-central1-f"
#  ]
  cluster    = "${google_container_cluster.fast_api_terraform_cluster.name}"
  
  node_count = "1"
  autoscaling {
    min_node_count = 0
    max_node_count = 1
  }

  management {
    auto_repair = true    # true の場合ノードが自動修復される
    auto_upgrade = true   # true の場合ノードが自動更新される
  }

  node_config {
    machine_type = "n1-standard-1"
    #machine_type = "n1-standard-4"
    
    #preemptible  = false         # プリミティブ VM
    #spot = true                  # Spot VM

    # デフォルトサービスアカウントが利用できる Google API のスコープ
    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append",
    ]

    # GPU ノードプールの場合
#    guest_accelerator {
#      type  = "nvidia-tesla-t4"
#      count = 1
#    }
  }
}
