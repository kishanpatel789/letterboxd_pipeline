terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.86"
    }
  }

  backend "local" {}
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

provider "snowflake" {
  profile = var.snowflake_profile
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

### SNOWFLAKE RESOURCES
resource "snowflake_database" "letterboxd_db" {
  name     = "LETTERBOXD"
  data_retention_time_in_days =  0
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.letterboxd_db.name
  name     = "RAW"
  data_retention_days = 0
}

resource "snowflake_schema" "staged" {
  database = snowflake_database.letterboxd_db.name
  name     = "STAGED"
  data_retention_days = 0
}

resource "snowflake_warehouse" "letterboxd_wh" {
  name           = "LETTERBOXD_WH"
  warehouse_type = "STANDARD"
  warehouse_size = "x-small"
  auto_resume = true
  auto_suspend= 3000
}