#-------------------------------
# プロバイダー設定
#-------------------------------
provider "aws" {
    profile = "${var.profile}"
    region = "${var.region}"
}

# EKS クラスターのリソース（resource "aws_eks_cluster"）使用時に必要
provider "kubernetes" {
  host                   = data.aws_eks_cluster.eks.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.eks.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.eks.token
}

#-------------------------------
# 実行する Terraform 環境情報
#-------------------------------
terraform {
  # terraform のバージョン
  #required_version = "~> 1.2.0"

  # バックエンドを S3 にする
  backend "s3" {
    bucket = "terraform-tf-states-bucket"
    key = "aws/eks/terraform.tfstate"
  }

  # 実行するプロバイダー
#  required_providers {
#    aws       = {
#      source  = "hashicorp/aws"
#      version = "~> 3.71.0"
#    }
#    kubernetes = {
#      version = "2.5.0"
#    }
#  }
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
    cidr_block = var.vpc_cidr_block
    enable_dns_hostnames = true
    enable_dns_support = true

    tags = {
      Name = "terraform-eks-vpc"
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    }
#    tags = "${merge(map("Name", "terraform-eks-subnet-${count.index+1}"), map("kubernetes.io/cluster/${var.cluster_name}", "owned"))}"
}

# サブネットワークの設定
resource "aws_subnet" "terraform_eks_subnet" {
    count = "${var.num_subnets}"                                                    # VPC の中にあるサブネットの数
    vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
    availability_zone = "${var.zone}"
    #cidr_block = "10.0.1.0/24"
    cidr_block              = "${cidrsubnet(var.vpc_cidr_block, 8, count.index)}"   # サブネットが２つ以上ある場合は、両方 cidr_block = "10.0.1.0/24" にすると conflicts するので、cidrsubnet() を使って各サブネットのCIDRがそれぞれ異なるようにする
    map_public_ip_on_launch = true                    # ?

    tags = {
      Name = "terraform-eks-subnet-${count.index+1}"
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    }
#    tags = "${merge(map("Name", "terraform-eks-subnet-${count.index+1}"), map("kubernetes.io/cluster/${var.cluster_name}", "owned"))}"
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
    count          = "${var.num_subnets}"                                             # リソースの数
    subnet_id      = "${element(aws_subnet.terraform_eks_subnet.*.id, count.index)}"  # element(リスト,要素番号) : リストの要素を取得 / aws_subnet.terraform_eks_subnet.* : 全ての aws_subnet リソースを参照 / count.index : リソースのインデックス
    route_table_id = "${aws_route_table.terraform_eks_route_table.id}"
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
# EKS クラスター
resource "aws_eks_cluster" "terraform_eks_cluster" {
  name     = "${var.cluster_name}"
  role_arn = "${aws_iam_role.terraform_eks_master_iam_role.arn}"    # master ノードの IAM role を割り当て
  version  = "${var.cluster_version}"

  # クラスタの VPC 設定
  vpc_config {
    security_group_ids = ["${aws_security_group.terraform_eks_master_security_group.id}"]
    subnet_ids = "${aws_subnet.terraform_eks_subnet.*.id}"
  }

	#
  depends_on = [
    "aws_iam_role_policy_attachment.terraform_eks_cluster_iam_policy_attachment",
    "aws_iam_role_policy_attachment.terraform_eks_service_iam_policy_attachment",
  ]
}

# オートスケール設定
#resource "aws_autoscaling_group" "terraform_eks_autoscaling_group" {
#  name                 = "EKS node autoscaling group"
#  desired_capacity     = "2"
#  launch_configuration = "${aws_launch_configuration.lc.id}"   # 必須パラメーター
#  max_size             = "1"
#  min_size             = "4"
#  vpc_zone_identifier = "${aws_subnet.terraform_eks_subnet.*.id}"

#  tag {
#    key                 = "Name"
#    value               = "terraform-eks-autoscaling-group"
#    propagate_at_launch = true
#  }

  # EKSで使用する場合は､EC2インスタンスには下記のタグが必須
#  tag {
#    key                 = "kubernetes.io/cluster/${var.cluster_name}"
#    value               = "owned"
#    propagate_at_launch = true
#  }
#}

#-------------------------------
# ノードプール
#-------------------------------
#resource "aws_eks_node_group" "terraform_eks_node_group" {
#  cluster_name    = aws_eks_cluster.terraform_eks_cluster.name
#  node_group_name = "terraform-eks-node-group"
#  node_role_arn   = aws_iam_role.iam_role002.arn
#  subnet_ids      = [var.subnet-a, var.subnet-c]
#  ami_type        = "AL2_x86_64"
#  instance_types  = ["t3.medium"]
  
#  remote_access {
#    ec2_ssh_key  = var.keyname
#    source_security_group_ids = [var.remote-sg]
#  }
 
#  scaling_config {
#    desired_size = 1
#    max_size     = 1
#    min_size     = 1
#  }
 
#  depends_on = [
#    aws_iam_role_policy_attachment.eks-node-group-node-policy,
#    aws_iam_role_policy_attachment.eks-node-group-cni-policy,
#    aws_iam_role_policy_attachment.eks-node-group-ecr-policy,
#  ]
#}
