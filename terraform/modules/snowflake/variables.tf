variable "snowflake_profile" {
  description = "Profile to be utilized in local Snowflake configuration"
  default     = "default"
  type        = string
}

variable "service_user_password" {
  description = "Password of service user in Snowflake"
  nullable = false
  type = string
}