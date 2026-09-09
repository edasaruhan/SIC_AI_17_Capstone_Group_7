variable "aws_region" {
  description = "AWS region selected after latency, residency and service review."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "availability_zones" {
  description = "Exactly two availability zones in aws_region."
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Provide exactly two availability zones."
  }
}

variable "certificate_arn" {
  description = "Validated ACM certificate for the public GrowthPilot domain."
  type        = string
}

variable "web_image" {
  description = "Immutable web container image reference, preferably by digest."
  type        = string
}

variable "backend_image" {
  description = "Immutable API/worker container image reference, preferably by digest."
  type        = string
}

variable "database_name" {
  type    = string
  default = "growthpilot"
}

variable "database_username" {
  type    = string
  default = "growthpilot_migrator"
}

variable "database_password" {
  description = "Bootstrap credential only; supply through a secure CI secret and rotate after provisioning."
  type        = string
  sensitive   = true
}

variable "redis_auth_token" {
  description = "At least 32 characters; supply through a secure CI secret."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.redis_auth_token) >= 32
    error_message = "Redis auth token must contain at least 32 characters."
  }
}

variable "desired_web_count" {
  type    = number
  default = 2
}

variable "desired_api_count" {
  type    = number
  default = 2
}

variable "desired_worker_count" {
  type    = number
  default = 1
}
