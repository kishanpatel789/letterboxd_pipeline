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

module "aws" {
  source = "./modules/aws"

  glue_service_role_arn           = var.glue_service_role_arn
  snowflake_service_user_username = module.snowflake.snowflake_service_user_username
  snowflake_service_user_password = var.snowflake_service_user_password
  snowflake_warehouse_name        = module.snowflake.snowflake_warehouse_name
}

module "snowflake" {
  source = "./modules/snowflake"

  service_user_password = var.snowflake_service_user_password
}