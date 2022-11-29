locals {
  envs = { for tuple in regexall("(.*)=(.*)", file("../.env")) : tuple[0] => sensitive(tuple[1]) }
}

resource "aws_s3_bucket" "temp_forecast" {
  bucket        = local.envs["TEMP_FORECAST_BUCKET_NAME"]
  force_destroy = true

  tags = {
    Name = local.envs["TEMP_FORECAST_BUCKET_NAME"]
  }
}

resource "aws_s3_bucket" "sdalc_temp_historical" {
  bucket        = local.envs["TEMP_HISTORICAL_BUCKET_NAME"]
  force_destroy = true

  tags = {
    Name = local.envs["TEMP_HISTORICAL_BUCKET_NAME"]
  }
}

resource "aws_s3_bucket" "sdalc_general" {
  bucket        = local.envs["GENERAL_BUCKET_NAME"]
  force_destroy = true

  tags = {
    Name = local.envs["GENERAL_BUCKET_NAME"]
  }
}

resource "aws_s3_bucket" "sdalc_demand" {
  bucket        = local.envs["DEMAND_BUCKET_NAME"]
  force_destroy = true

  tags = {
    Name = local.envs["DEMAND_BUCKET_NAME"]
  }
}

resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id          = aws_vpc.main_vpc.id
  service_name    = "com.amazonaws.${var.region}.s3"
  route_table_ids = [aws_route_table.public_route_table.id, aws_route_table.private_route_table.id]
}