# Setting Up a Linux Virtual Machine on Azure from Windows

## Prerequisites
- An active Azure subscription
- A Windows computer
- Web browser
- Windows Terminal, PowerShell, or Git Bash installed
- WSL (Windows Subsystem for Linux) installed (optional but recommended)

## Steps

### 1. Set Up SSH on Windows
1. Open PowerShell as Administrator and check if OpenSSH is installed:
```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
```

1. If not installed, install OpenSSH:
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

1. Generate SSH key (choose one method):

   Using PowerShell:
   ```powershell
   ssh-keygen -t rsa -b 4096
   # Keys will be saved to C:\Users\YourUsername\.ssh\
   ```

   Using Git Bash:
   ```bash
   ssh-keygen -t rsa -b 4096
   # Keys will be saved to C:/Users/YourUsername/.ssh/
   ```

### Sign into Azure Portal
1. Navigate to portal.azure.com in your browser
1. Log in with your Azure credentials

### Create a Resource Group
1. Click "Resource Groups" in the left sidebar
1. Click "+ Create" at the top
1. Fill in the required fields:
    - Subscription: Select your subscription
    - Resource group name: Choose a descriptive name (e.g., "linux-prod")
    - Region: Select the closest datacenter to your location
1. Click "Review + Create" then "Create"

### 4. Create the Linux Virtual Machine
1. Click "+ Create a resource" in the left sidebar
1. Search for and select "Virtual Machine"
1. Configure the basic settings:
    - Resource group: Select the one you just created
    - Virtual machine name: Choose a unique name (e.g., "linux-web")
    - Region: Same as your resource group
    - Image: Select Ubuntu Server 22.04 LTS (or your preferred Linux distro)
    - Size: Choose based on your workload needs
1. Authentication:
    - Authentication type: Choose "SSH public key"
    - Username: Create a username
    - SSH public key source: "Use existing public key"
    - Copy the contents of your public key file:

```powershell
# In PowerShell, view your public key:
Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
```

1. Networking:
    - Virtual network: Create new or select existing
    - Public IP: Create new
    - NIC network security group: Basic
    - Public inbound ports: Allow SSH (22)

### Review and Create
1. Review your configuration
1. Check the estimated cost
1. Click "Create"
1. Wait for deployment to complete

### Connect to Your Linux VM from Windows

#### Using PowerShell
1. Get your VM's public IP from Azure portal:
    - Go to your VM resource
    - Copy the public IP address from the overview page

1. Connect using SSH:

```powershell
ssh username@public-ip-address
# Example: ssh azureuser@20.30.40.50
```

#### Using Windows Terminal
1. Open Windows Terminal
1. Start a new PowerShell tab
1. Use the same SSH command as above

#### Using Git Bash
1. Open Git Bash
1. Connect using:

```bash
ssh -i ~/.ssh/id_rsa username@public-ip-address
```

### Common Issues for Windows Users

1. SSH key permissions too open:
   In PowerShell:
   ```powershell
   # Check current permissions
   Get-Acl ~\.ssh\id_rsa

   # Reset permissions (run as administrator)
   icacls $env:USERPROFILE\.ssh\id_rsa /inheritance:r /grant:r "$($env:USERNAME):(R)"
   ```

1. Connection timed out:
    - Check if port 22 is open in your Network Security Group
    - Verify the VM is running
    - Test connection:

```powershell
Test-NetConnection -ComputerName public-ip-address -Port 22
```

1. Key format issues:
    - Ensure the key is in OpenSSH format
    - Check for extra line breaks or spaces in your public key

## File Transfer from Windows to Linux VM

1. Using SCP in PowerShell:
```powershell
scp C:\path\to\local\file username@public-ip-address:/home/username/
```

1. Using WinSCP:
    - Download and install WinSCP
    - Create new connection using your VM's IP and credentials
    - Drag and drop files between Windows and Linux

### 9. Basic Linux Commands for Windows Users
```bash
# List files (like 'dir' in Windows)
ls

# Change directory (same as Windows)
cd /path/to/directory

# Create directory (like 'mkdir' in Windows)
mkdir newfolder

# View file content (like 'type' in Windows)
cat filename

# Edit text file
nano filename
```

Remember to replace `username`, `public-ip-address`, and `YourUsername` with your actual values.
