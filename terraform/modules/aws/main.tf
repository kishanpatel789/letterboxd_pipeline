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
  name                    = "letterboxd_snowflake_service_user"
  recovery_window_in_days = 0
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

resource "aws_glue_crawler" "example" { # TODO: CHANGE RESOURCE NAME
  database_name = aws_glue_catalog_database.glue_db.name
  name          = "letterboxd_crawler"
  role          = var.glue_service_role_arn

  s3_target {
    path = "s3://${aws_s3_bucket.bucket_data_lake.bucket}/raw/"
  }
}

resource "aws_glue_job" "glue_job" {
  name              = "publish_letterboxd_to_snowflake_tf"
  role_arn          = var.glue_service_role_arn
  connections       = ["Snowflake_Letterboxd"]
  glue_version      = "4.0"
  max_retries       = 0
  timeout           = 10
  worker_type       = "G.1X"
  number_of_workers = 2

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.bucket_data_lake.bucket}/scripts/publish_to_snowflake.py"
    python_version  = "3"
  }

  execution_property {
    max_concurrent_runs = 1
  }

  default_arguments = {
    "--spark-event-logs-path"            = "s3://${aws_s3_bucket.bucket_data_lake.bucket}/sparkHistoryLogs/",
    "--enable-job-insights"              = "false",
    "--enable-glue-datacatalog"          = "true",
    "--enable-continuous-cloudwatch-log" = "true",
    "--job-bookmark-option"              = "job-bookmark-disable",
    "--job-language"                     = "python",
    "--TempDir"                          = "s3://${aws_s3_bucket.bucket_data_lake.bucket}/temporary/",
    "--enable-auto-scaling"              = "true"
  }
}
