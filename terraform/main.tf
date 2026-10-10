
provider "aiven" {
  api_token = var.aiven_api_token
}

resource "aiven_pg" "mortalidade_materna" {
  project      = var.project_name
  cloud_name = "do-nyc"
  plan         = "free-1-1gb"
  service_name = var.service_name
}
