variable "snowflake_service_user_password" {
  description = "Password of service user in Snowflake"
  nullable    = false
  type        = string
}

variable "glue_service_role_arn" {
  description = "ARN of GlueServiceRole"
  nullable    = false
  type        = string
}