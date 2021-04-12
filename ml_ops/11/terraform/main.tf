# プロバイダーの設定
provider "aws" {
    version = "~> 2.0"
    profile = "Yagami360"
    region = "us-west-2"
}

# VPC の設定
resource "aws_vpc" "terraform_vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support = true
    tags = {
        Name = "terraform_vpc"
    }
}

# サブネットワークの設定
resource "aws_subnet" "terraform_subnet" {
    #cidr_block = "10.1.1.0/24"
    cidr_block = "${cidrsubnet(aws_vpc.terraform_vpc.cidr_block, 3, 1)}"
    vpc_id = "${aws_vpc.terraform_vpc.id}"
    availability_zone = "us-west-2a"
}

# ゲートウェイの設定
resource "aws_internet_gateway" "terraform_gateway" {
    vpc_id = "${aws_vpc.terraform_vpc.id}"
}

# ルーティングテーブルの設定
resource "aws_route_table" "terraform_route_table" {
    vpc_id = "${aws_vpc.terraform_vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.terraform_gateway.id}"
    }
}

resource "aws_route_table_association" "terraform_route_table_association" {
    subnet_id = "${aws_subnet.terraform_subnet.id}"
    route_table_id = "${aws_route_table.terraform_route_table.id}"
}

# セキュリティーグループの設定
resource "aws_security_group" "terraform_security_group" {
    name = "terraform_security_group"
    description = "Used in the terraform"
    ingress {
        from_port = 22 #適宜変更
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# 固定 IP の設定
resource "aws_eip" "terraform_eip" {
    instance = "${aws_instance.terraform_instance[0].id}"
    vpc = true
}

# EC2インスタンスの設定
resource "aws_instance" "terraform_instance" {
    count         = 2
    ami           = "ami-008b09448b998a562" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
    instance_type = "t2.micro"
    vpc_security_group_ids = ["${aws_security_group.terraform_security_group.id}"]
    subnet_id = "${aws_subnet.terraform_subnet.id}"
    tags = {
        Name = "${format("terraform_instance-%02d", count.index + 1)}"
    }
}
