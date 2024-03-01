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
}

module "snowflake" {
  source = "./modules/snowflake"

  service_user_password = var.snowflake_service_user_password
}