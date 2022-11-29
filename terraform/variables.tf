variable "key_name" {
  default = "vockey"
  type    = string
}

variable "availability_zones" {
  default = ["us-east-1a", "us-east-1b"]
  type    = list(string)
}

variable "vpc_cidr_block" {
  default = "10.0.0.0/16"
  type    = string
}

variable "region" {
  default = "us-east-1"
  type    = string
}

variable "pem_file_dir" {
  default = "~/Downloads/keys.pem"
  type    = string
}