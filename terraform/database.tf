resource "aws_db_subnet_group" "private_subnets_group" {
  name        = "private_subnets"
  subnet_ids  = aws_subnet.private_subnets[*].id
  description = "Private subnets group"
  tags = {
    Name = "Private subnets"
  }
}

resource "aws_db_instance" "postgresdb" {
  instance_class          = "db.t3.micro"
  allocated_storage       = 5
  engine                  = "postgres"
  engine_version          = "13"
  skip_final_snapshot     = true
  availability_zone       = var.availability_zones[0]
  db_subnet_group_name    = aws_db_subnet_group.private_subnets_group.name
  vpc_security_group_ids  = [aws_security_group.database_security_group.id]
  db_name                 = local.envs["DATABASE_NAME"]
  username                = local.envs["DATABASE_USER"]
  password                = local.envs["DATABASE_PASSWORD"]
  monitoring_interval     = 0
  storage_type            = "gp2"
  identifier              = "postgresdb"
  backup_retention_period = 7
  backup_window           = "01:00-02:00"
}

resource "aws_security_group" "database_security_group" {
  name   = "database_security_group"
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    cidr_blocks = [var.vpc_cidr_block]
    from_port   = 5432
    protocol    = "tcp"
    to_port     = 5432
  }

  egress {
    cidr_blocks = [var.vpc_cidr_block]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  tags = {
    Name    = "database_security_group"
    Project = "electrical demand"
  }
}