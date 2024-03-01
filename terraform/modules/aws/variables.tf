variable "region" {
  description = "Region for AWS resoures."
  default     = "us-east-1"
  type        = string
}

variable "aws_profile" {
  description = "Profile to be utilized in local AWS CLI configuration"
  default     = "default"
  type        = string
}

variable "bucket_name" {
  description = "Name of S3 bucket; must be globally unique"
  default     = "letterboxd-data-kpde"
  type        = string
}

variable "snowflake_service_user_username" {
  description = "Username of service user in Snowflake"
  nullable = false
  type = string
}

variable "snowflake_service_user_password" {
  description = "Password of service user in Snowflake"
  nullable = false
  type = string
}

variable "snowflake_warehouse_name" {
  description = "Name of virtual warehouse in Snowflake"
  nullable = false
  type = string
}