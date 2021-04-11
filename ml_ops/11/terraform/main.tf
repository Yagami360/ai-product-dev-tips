# プロバイダーの設定
provider "aws" {
    version = "~> 2.0"
    profile = "Yagami360"
    region = "us-west-2"
}

# EC2インスタンスの設定
resource "aws_instance" "terraform_instance" {
    count         = 2
    ami           = "ami-008b09448b998a562" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
    instance_type = "t2.micro"

    tags = {
        Name = "${format("terraform_instance-%02d", count.index + 1)}"
    }
}

# VPC の設定
resource "aws_vpc" "terraform_vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support = true
    tags {
        Name = "terraform_vpc"
    }
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
