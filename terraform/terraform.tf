terraform {
  required_version = "1.9.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.79.0"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.credentials_profile

  default_tags {
    tags = {
      Terraform = "True"
    }
  }
}
