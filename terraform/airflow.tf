resource "aws_instance" "airflow" {
  ami                    = "ami-0b0dcb5067f052a63"
  instance_type          = "t2.large"
  availability_zone      = var.availability_zones[0]
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.airflow_security_group.id]
  subnet_id              = aws_subnet.public_subnet_1.id
  iam_instance_profile   = aws_iam_instance_profile.airflow_profile.name
  root_block_device {
    volume_size = 30
  }
  user_data = <<EOF
    #!/bin/bash
    set -x
    yum update -y
    amazon-linux-extras install docker -y
    service docker start
    systemctl enable docker
    usermod -a -G docker ec2-user
    chmod 666 /var/run/docker.sock
    curl -SL https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
  EOF
  tags = {
    Name    = "airflow"
    Project = "electrical demand"
  }
}

resource "aws_iam_instance_profile" "airflow_profile" {
  name = "airflow_profile"
  role = data.aws_iam_role.main_role.name
}

resource "null_resource" "airflow" {
  provisioner "file" {
    source      = "../scripts/dags"
    destination = "/home/ec2-user/dags"
  }
  provisioner "file" {
    source      = "../data"
    destination = "/home/ec2-user/data"
  }
  provisioner "file" {
    source      = "../.env"
    destination = "/home/ec2-user/.env"
  }
  provisioner "file" {
    source      = "../scripts/docker-compose.yaml"
    destination = "/home/ec2-user/docker-compose.yaml"
  }
  provisioner "file" {
    source      = "../scripts/Dockerfile_dashboard"
    destination = "/home/ec2-user/Dockerfile_dashboard"
  }
  provisioner "file" {
    source      = "../scripts/Dockerfile_database_api"
    destination = "/home/ec2-user/Dockerfile_database_api"
  }
  provisioner "file" {
    source      = "../scripts/airflow_image"
    destination = "/home/ec2-user/airflow_image"
  }
  provisioner "file" {
    source      = "~/.aws"
    destination = "/home/ec2-user/.aws"
  }
  provisioner "remote-exec" {
    inline = [
      "sudo cloud-init status --wait",
      "alias aws2=/usr/local/bin/aws",
      "echo \"DEMAND_DOCKER_IMAGE=${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}\" >> .env",
      # "echo \"DATABASE_API_DOCKER_IMAGE=${aws_ecr_repository.database_api.repository_url}:${local.envs["DATABASE_API_DOCKER_IMAGE_TAG"]}\" >> .env",
      # "echo \"DASHBOARD_DOCKER_IMAGE=${aws_ecr_repository.dashboard.repository_url}:${local.envs["DASHBOARD_DOCKER_IMAGE_TAG"]}\" >> .env",
      "echo \"DATABASE_HOST=${aws_db_instance.postgresdb.endpoint}\" >> .env",
      "mkdir versions plugins logs",
      "aws2 ecr get-login-password | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com",
      "docker pull ${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}",
      # "docker pull ${aws_ecr_repository.database_api.repository_url}:${local.envs["DATABASE_API_DOCKER_IMAGE_TAG"]}",
      # "docker pull ${aws_ecr_repository.dashboard.repository_url}:${local.envs["DASHBOARD_DOCKER_IMAGE_TAG"]}",
      "docker-compose up -d",
    ]
  }
  connection {
    host        = aws_instance.airflow.public_ip
    type        = "ssh"
    user        = "ec2-user"
    password    = ""
    private_key = file(var.pem_file_dir)
  }
  depends_on = [
    docker_registry_image.demand
    # docker_registry_image.database_api,
    # docker_registry_image.dashboard
  ]
}

resource "aws_security_group" "airflow_security_group" {
  name   = "airflow_security_group"
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  tags = {
    Name    = "airflow_security_group"
    Project = "electrical demand"
  }
}