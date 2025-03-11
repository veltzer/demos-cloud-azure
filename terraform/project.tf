provider "azurerm" {
	features {}
	subscription_id = "3f79a68d-cf0d-4291-a31f-185897f7fda1"
}

resource "azurerm_resource_group" "mark_rg_id" {
	name     = "mark_rg_name"
	location = "East US"
}
