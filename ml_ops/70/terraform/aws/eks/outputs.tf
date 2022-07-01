locals {
  # <<EOF ~ EOF（ヒアドキュメント）で kubeconfig のk8s マニフェスト（yml形式）を定義
	# kubeconfig : どのクラスターにどのユーザーとして接続するのかの接続設定した k8s マニフェストファイル。通常は $HOME/.kube/config に存在するが、terraform で EKS クラスター作成
  kubeconfig = <<EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: ${aws_eks_cluster.terraform_eks_cluster.endpoint}
    certificate-authority-data: ${aws_eks_cluster.terraform_eks_cluster.certificate_authority.0.data}
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "${local.cluster_name}"
EOF

	# master と node を紐づけるための？ ConfigMap リソースを定義
  eks_configmap = <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: ${aws_iam_role.terraform_eks_node_iam_role.arn}
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
EOF
}

output "kubeconfig" {
  value = "${local.kubeconfig}"
}

output "eks_configmap" {
  value = "${local.eks_configmap}"
}