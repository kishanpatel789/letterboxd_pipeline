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

# database, schemas, warehouse
resource "snowflake_database" "letterboxd_db" {
  name                        = "LETTERBOXD"
  data_retention_time_in_days = 0
}

resource "snowflake_schema" "raw" {
  database            = snowflake_database.letterboxd_db.name
  name                = "RAW"
  data_retention_days = 0
}

resource "snowflake_schema" "staged" {
  database            = snowflake_database.letterboxd_db.name
  name                = "STAGED"
  data_retention_days = 0
}

resource "snowflake_warehouse" "letterboxd_wh" {
  name           = "LETTERBOXD_WH"
  warehouse_type = "STANDARD"
  warehouse_size = "x-small"
  auto_resume    = true
  auto_suspend   = 1200
}

# user and role
resource "snowflake_user" "svc_letterboxd" {
  name              = "SVC_LETTERBOXD"
  password          = var.service_user_password
  default_warehouse = snowflake_warehouse.letterboxd_wh.name
  default_role      = snowflake_role.svc_letterboxd_role.name
  default_namespace = snowflake_database.letterboxd_db.name
}

resource "snowflake_role" "svc_letterboxd_role" {
  name = "SVC_LETTERBOXD_ROLE"
}

resource "snowflake_grant_account_role" "grant_role" {
  role_name = snowflake_role.svc_letterboxd_role.name
  user_name = snowflake_user.svc_letterboxd.name
}

# service role privileges
resource "snowflake_grant_privileges_to_account_role" "db_usage" {
  privileges        = ["USAGE"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.letterboxd_db.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "schema_usage" {
  privileges        = ["USAGE", "MODIFY", "CREATE TABLE", "CREATE VIEW"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_schema {
    all_schemas_in_database = snowflake_database.letterboxd_db.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "table_privileges_raw" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_privileges_raw" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "table_privileges_staged" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.staged.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_privileges_staged" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = snowflake_role.svc_letterboxd_role.name
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.staged.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "warehouse_privileges" {
  privileges = ["USAGE"]
  account_role_name  = snowflake_role.svc_letterboxd_role.name
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.letterboxd_wh.name
  }
}

# sysadmin privileges
resource "snowflake_grant_privileges_to_account_role" "table_privileges_raw_sysadmin" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = "SYSADMIN"
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_privileges_raw_sysadmin" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = "SYSADMIN"
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "table_privileges_staged_sysadmin" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = "SYSADMIN"
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.staged.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_privileges_staged_sysadmin" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = "SYSADMIN"
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.letterboxd_db.name}\".\"${snowflake_schema.staged.name}\""
    }
  }
}