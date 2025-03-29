#!/usr/bin/env python
"""
Script to delete all library variable groups in an Azure DevOps project using the Azure CLI.
"""

import subprocess
import json
import argparse
import sys
import time

def ensure_devops_extension():
    """Ensure Azure DevOps CLI extension is installed."""
    try:
        # Check if extension is installed
        result = subprocess.run(
            ['az', 'extension', 'list', '--query', "[?name=='azure-devops']"],
            capture_output=True, text=True, check=True
        )
        
        if '[]' in result.stdout:
            print("Azure DevOps CLI extension not found. Installing...")
            install_result = subprocess.run(
                ['az', 'extension', 'add', '--name', 'azure-devops'],
                capture_output=True, text=True
            )
            if install_result.returncode != 0:
                print(f"Failed to install Azure DevOps extension: {install_result.stderr}")
                print("Please install it manually: az extension add --name azure-devops")
                sys.exit(1)
            print("Azure DevOps CLI extension installed successfully.")
        else:
            print("Azure DevOps CLI extension is already installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking Azure CLI extensions: {e}")
        sys.exit(1)

def configure_devops_defaults(organization):
    """Configure Azure DevOps CLI defaults."""
    try:
        print(f"Setting default organization to https://dev.azure.com/{organization}/")
        result = subprocess.run(
            ['az', 'devops', 'configure', '--defaults', f'organization=https://dev.azure.com/{organization}/'],
            capture_output=True, text=True, check=True
        )
        print("Default organization configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring Azure DevOps defaults: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def list_variable_groups(project):
    """List all variable groups in the specified project using Azure CLI."""
    try:
        print(f"Fetching variable groups from project '{project}'...")
        result = subprocess.run(
            ['az', 'pipelines', 'variable-group', 'list', '--project', project, '--output', 'json'],
            capture_output=True, text=True, check=True
        )
        
        variable_groups = json.loads(result.stdout)
        return variable_groups
    except subprocess.CalledProcessError as e:
        print(f"Error listing variable groups: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def delete_variable_group(group_id, project):
    """Delete a specific variable group by ID."""
    try:
        result = subprocess.run(
            ['az', 'pipelines', 'variable-group', 'delete', '--group-id', str(group_id),
             '--project', project, '--yes'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception during variable group deletion: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Delete all library variable groups in an Azure DevOps project")
    parser.add_argument("--organization", "-o", required=True, help="Azure DevOps organization name")
    parser.add_argument("--project", "-p", required=True, help="Azure DevOps project name")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt and delete all variable groups")
    parser.add_argument("--exclude", "-e", nargs="+", help="List of variable group names to exclude from deletion")
    
    args = parser.parse_args()
    
    # Ensure Azure DevOps CLI extension is installed
    ensure_devops_extension()
    
    # Configure default organization
    configure_devops_defaults(args.organization)
    
    # Get list of variable groups
    variable_groups = list_variable_groups(args.project)
    
    if not variable_groups:
        print("No variable groups found in the project.")
        return
    
    exclude_list = args.exclude or []
    groups_to_delete = [group for group in variable_groups if group["name"] not in exclude_list]
    excluded_groups = [group for group in variable_groups if group["name"] in exclude_list]
    
    print(f"Found {len(variable_groups)} variable groups in the project.")
    print(f"{len(groups_to_delete)} will be deleted.")
    
    if excluded_groups:
        print("Excluded variable groups:")
        for group in excluded_groups:
            print(f"- {group['name']}")
    
    if not groups_to_delete:
        print("No variable groups to delete after applying exclusions.")
        return
    
    print("\nVariable groups to delete:")
    for group in groups_to_delete:
        print(f"- {group['name']} (ID: {group['id']})")
    
    # Confirm deletion
    if not args.confirm:
        confirm = input("\nAre you sure you want to delete these variable groups? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Delete variable groups
    print("\nDeleting variable groups...")
    success_count = 0
    for group in groups_to_delete:
        print(f"Deleting {group['name']}...", end="", flush=True)
        if delete_variable_group(group['id'], args.project):
            print(" Success")
            success_count += 1
        else:
            print(" Failed")
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\nDeleted {success_count} out of {len(groups_to_delete)} variable groups.")

if __name__ == "__main__":
    main()
