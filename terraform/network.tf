resource "aws_vpc" "main_vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  tags = {
    Name    = "main_vpc"
    Project = "electrical demand"
  }
}

resource "aws_subnet" "public_subnet_1" {
  cidr_block              = cidrsubnet(var.vpc_cidr_block, 8, 0)
  vpc_id                  = aws_vpc.main_vpc.id
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true
  tags = {
    Name    = "public_subnet_subnet_1"
    Project = "electrical demand"
  }
}

resource "aws_internet_gateway" "main_vpc_igw" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name    = "main_vpc_igw"
    Project = "electrical demand"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_vpc_igw.id
  }
  tags = {
    Name    = "public_route_table"
    Project = "electrical demand"
  }
}

resource "aws_route_table_association" "public_subnet_route_table_association" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_subnet" "private_subnets" {
  count                   = length(var.availability_zones)
  cidr_block              = cidrsubnet(var.vpc_cidr_block, 8, count.index * 2 + 1)
  vpc_id                  = aws_vpc.main_vpc.id
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false
  tags = {
    Name    = "private_subnet_${count.index}"
    Project = "electrical demand"
  }
}

resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name    = "private_route_table"
    Project = "electrical demand"
  }
}

resource "aws_route_table_association" "private_subnets_route_table_association" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private_subnets[count.index].id
  route_table_id = aws_route_table.private_route_table.id
}