terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

# s3 bucket for data lake
resource "aws_s3_bucket" "bucket_data_lake" {
  bucket        = var.bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption_data_lake" {
  bucket = aws_s3_bucket.bucket_data_lake.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_data_lake" {
  bucket = aws_s3_bucket.bucket_data_lake.id

  rule {
    id = "lifecycle-global"

    filter {}

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }

    expiration {
      days = 120
    }
  }
}

# secrets manager for snowflake service user
resource "aws_secretsmanager_secret" "snowflake_service_user" {
  name = "letterboxd_snowflake_service_user"
}

resource "aws_secretsmanager_secret_version" "example" {
  secret_id     = aws_secretsmanager_secret.snowflake_service_user.id
  secret_string = <<-EOT
    {
      "sfUser": "${var.snowflake_service_user_username}",
      "sfPassword": "${var.snowflake_service_user_password}",
      "sfWarehouse": "${var.snowflake_warehouse_name}"
    }
  EOT
}

# glue resources
resource "aws_glue_catalog_database" "glue_db" {
  name = "letterboxd_db"
}

resource "aws_glue_crawler" "example" {
  database_name = aws_glue_catalog_database.glue_db.name
  name          = "letterboxd_crawler"
  role          = "arn:aws:iam::655268872845:role/service-role/AWSGlueServiceRole"

  s3_target {
    path = "s3://${aws_s3_bucket.bucket_data_lake.bucket}/raw/"
  }
}