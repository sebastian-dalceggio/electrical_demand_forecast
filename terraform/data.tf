data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}