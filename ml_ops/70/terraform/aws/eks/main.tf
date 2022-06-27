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
# EKS の master ノード用の IAM role
resource "aws_iam_role" "terraform_eks_master_iam_role" {
  name = "terraform-eks-master-iam-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

# EKS の master ノード用の IAM role に IAM policy（EKSクラスターのARN）を割り当て 
resource "aws_iam_role_policy_attachment" "terraform_eks_cluster_iam_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = "${aws_iam_role.terraform_eks_master_iam_role.name}"
}

# EKS の master ノード用の IAM role に IAM policy（EKSサービズのARN）を割り当て 
resource "aws_iam_role_policy_attachment" "terraform_eks_service_iam_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = "${aws_iam_role.terraform_eks_master_iam_role.name}"
}

# EKS の master ノード以外のノード用の IAM role
resource "aws_iam_role" "terraform_eks_node_iam_role" {
  name = "terraform-eks-node-iam-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

# EKS の master ノード以外のノード用の IAM role に IAM policy（AmazonEKSWorkerNodePolicyのARN）を割り当て 
resource "aws_iam_role_policy_attachment" "terraform_eks_worker_node_iam_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
}

# EKS の master ノード以外のノード用の IAM role に IAM policy（AmazonEKS_CNI_PolicyのARN）を割り当て
resource "aws_iam_role_policy_attachment" "terraform_eks_cni_iam_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
}

# EKS の master ノード以外のノード用の IAM role に IAM policy（AmazonEC2ContainerRegistryReadOnlyのARN）を割り当て
resource "aws_iam_role_policy_attachment" "terraform_eks_ro_iam_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
}

# EKS の master ノード以外のノード用のインスタンスプロファイル。IAM ロールを EC2 インスタンスに紐つけるために必要
resource "aws_iam_instance_profile" "terraform_eks_node_iam_instance_profile" {
  name = "terraform-eks-node-iam-instance-profile"
  role = "${aws_iam_role.terraform_eks_node_iam_role.name}"
}

#-------------------------------
# VPC
#-------------------------------
# VPC の設定
resource "aws_vpc" "terraform_eks_vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support = true
    tags = {
        Name = "terraform-eks-vpc"
    }
}

# サブネットワークの設定
resource "aws_subnet" "terraform_eks_subnet" {
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
    cidr_block = "10.0.1.0/24"
    availability_zone = "us-west-2a"
    tags = {
        Name = "terraform-eks-subnet"
    }
}

# ゲートウェイの設定
resource "aws_internet_gateway" "terraform_eks_gateway" {
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
    tags = {
        Name = "terraform-eks-gateway"
    }
}

# ルーティングテーブルの設定
resource "aws_route_table" "terraform_eks_route_table" {
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.terraform_eks_gateway.id}"
    }
    tags = {
        Name = "terraform-eks-route-table"
    }
}

resource "aws_route_table_association" "terraform_eks_route_table_association" {
    subnet_id = "${aws_subnet.terraform_eks_subnet.id}"
    route_table_id = "${aws_route_table.terraform_eks_route_table.id}"
    tags = {
        Name = "terraform-eks-route-table-association"
    }
}

# マスターノード用のセキュリティーグループの設定
resource "aws_security_group" "terraform_eks_master_security_group" {
    name = "terraform-eks-master-security-group"
    description = "EKS master security group"
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
    # インバウンドルール(SSL通信ではHTTPSプロトコルにあたる443番を利用)
    ingress {
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    # アウトバウンドルール(全開放)
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "terraform-eks-master-security-group"
    }
}

# マスターノード以外の各ノード用のセキュリティーグループの設定
resource "aws_security_group" "terraform_eks_nodes_security_group" {
    name = "terraform-eks-nodes-security-group"
    description = "EKS node security group"
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"

    # インバウンドルール()
    ingress {
        description     = "Allow cluster master to access cluster node"
        from_port = 1025
        to_port = 65535
        protocol = "tcp"
        #cidr_blocks = ["0.0.0.0/0"]
        security_groups = ["${aws_security_group.terraform_eks_master_security_group.id}"]  # master ノードのセキュリティーグループ
    }
    # インバウンドルール(masterノードとの通信用<TCP/443>)
    ingress {
        description     = "Allow cluster master to access cluster node"
        from_port = 443
        to_port = 443
        protocol = "tcp"
        #cidr_blocks = ["0.0.0.0/0"]    # ? 不要
        security_groups = ["${aws_security_group.terraform_eks_master_security_group.id}"]  # master ノードのセキュリティーグループ
        self            = false     # ?
    }
    # インバウンドルール(pod間通信用)
    ingress {
        description = "Allow inter pods communication"
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        self        = true
    }
    # アウトバウンドルール(全開放)
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "terraform-eks-nodes-security-group"
    }
}

#-------------------------------
# EKS クラスター
#-------------------------------

#-------------------------------
# ノードプール
#-------------------------------
