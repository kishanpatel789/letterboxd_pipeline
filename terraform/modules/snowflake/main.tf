terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.86"
    }
  }
}

provider "snowflake" {
  profile = var.snowflake_profile
}

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