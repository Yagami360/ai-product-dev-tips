# プロバイダーの設定
provider "aws" {
    #version = "~> 2.0"
    #profile = "default"
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
    vpc_id = "${aws_vpc.terraform_vpc.id}"
    #vpc_id = aws_vpc.terraform_vpc.id
    cidr_block = "10.0.1.0/24"
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
    vpc_id = "${aws_vpc.terraform_vpc.id}"
    # インバウンドルール(ssh接続用)
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    # インバウンドルール(pingでの接続確認用)
    ingress {
        from_port = -1
        to_port = -1
        protocol = "icmp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    # アウトバウンドルール(全開放)
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# 固定 IP の設定
resource "aws_eip" "terraform_eip" {
    instance = "${aws_instance.terraform_instance[0].id}"
    vpc = true
}

# ssh-key 登録
resource "aws_key_pair" "terraform_key_pair" {
    key_name   = "id_rsa"
    public_key = file("/.ssh/id_rsa.pub")
}

# EC2インスタンスの設定
resource "aws_instance" "terraform_instance" {
    count         = 2
    ami           = "ami-008b09448b998a562" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
    instance_type = "t2.micro"
    vpc_security_group_ids = ["${aws_security_group.terraform_security_group.id}"]
    subnet_id = "${aws_subnet.terraform_subnet.id}"
    associate_public_ip_address = "true"
    key_name      = aws_key_pair.terraform_key_pair.id
    tags = {
        Name = "${format("terraform_instance-%02d", count.index + 1)}"
    }
}

