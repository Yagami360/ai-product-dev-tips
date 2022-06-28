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

variable "cluster_name" {
  default = "terraform-eks-cluster"
}

variable "cluster_version" {
  default = "1.10"
}
