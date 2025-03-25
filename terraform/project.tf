provider "azurerm" {
	features {}
}

resource "azurerm_resource_group" "mark_rg_id" {
	name = "mark_rg_name"
	location = "East US"
}

resource "azurerm_virtual_network" "mark_vn_id" {
	name                = "mark_vn_name"
	address_space       = ["10.0.0.0/16"]
	location            = azurerm_resource_group.mark_rg_id.location
	resource_group_name = azurerm_resource_group.mark_rg_id.name
	tags = {
		environment = "Production"
	}
}

resource "azurerm_subnet" "mark_subnet_id" {
  name                 = "mark_subnet_name"
  resource_group_name  = azurerm_resource_group.mark_rg_id.name
  virtual_network_name = azurerm_virtual_network.mark_vn_id.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "mark_public_ip_id" {
  name                = "mark_public_ip_name"
  sku                 = "Basic"
  location            = azurerm_resource_group.mark_rg_id.location
  resource_group_name = azurerm_resource_group.mark_rg_id.name
  allocation_method   = "Dynamic"
}

resource "azurerm_network_interface" "mark_network_interface_id" {
  name                = "mark_network_interface_name"
  location            = azurerm_resource_group.mark_rg_id.location
  resource_group_name = azurerm_resource_group.mark_rg_id.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.mark_subnet_id.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.mark_public_ip_id.id
  }
}

resource "azurerm_linux_virtual_machine" "mark_vm_id" {
  name                = "mark_vm_name"
  computer_name       = "markvm"
  resource_group_name = azurerm_resource_group.mark_rg_id.name
  location            = azurerm_resource_group.mark_rg_id.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.mark_network_interface_id.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_personal.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
}
