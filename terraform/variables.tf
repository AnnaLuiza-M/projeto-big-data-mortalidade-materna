
variable "aiven_api_token" {
  description = "Token de API da Aiven"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Nome do projeto na Aiven"
  type        = string
  default     = "ucsal-c9df"
}

variable "service_name" {
  description = "Nome do serviço PostgreSQL"
  type        = string
  default     = "mortalidade-materna-db"
}
