#!/usr/bin/env python
"""
Script to delete all Git repositories in an Azure DevOps project using the Azure CLI.
This script uses 'az repos' commands directly instead of REST API calls.
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

def list_repositories(project):
    """List all Git repositories in the specified project using Azure CLI."""
    try:
        print(f"Fetching repositories from project '{project}'...")
        result = subprocess.run(
            ['az', 'repos', 'list', '--project', project, '--output', 'json'],
            capture_output=True, text=True, check=True
        )
        
        repos = json.loads(result.stdout)
        return repos
    except subprocess.CalledProcessError as e:
        print(f"Error listing repositories: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def delete_repository(repo_id, project):
    """Delete a specific Git repository by ID using Azure CLI."""
    try:
        result = subprocess.run(
            ['az', 'repos', 'delete', '--id', repo_id, '--project', project, '--yes'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception during repository deletion: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Delete all Git repositories in an Azure DevOps project using Azure CLI")
    parser.add_argument("--organization", "-o", required=True, help="Azure DevOps organization name")
    parser.add_argument("--project", "-p", required=True, help="Azure DevOps project name")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt and delete all repositories")
    parser.add_argument("--exclude", "-e", nargs="+", help="List of repository names to exclude from deletion")
    
    args = parser.parse_args()
    
    # Ensure Azure DevOps CLI extension is installed
    ensure_devops_extension()
    
    # Configure default organization
    configure_devops_defaults(args.organization)
    
    # Get list of repositories
    repositories = list_repositories(args.project)
    
    if not repositories:
        print("No repositories found in the project.")
        return
    
    exclude_list = args.exclude or []
    repos_to_delete = [repo for repo in repositories if repo["name"] not in exclude_list]
    excluded_repos = [repo for repo in repositories if repo["name"] in exclude_list]
    
    print(f"Found {len(repositories)} repositories in the project.")
    print(f"{len(repos_to_delete)} will be deleted.")
    
    if excluded_repos:
        print("Excluded repositories:")
        for repo in excluded_repos:
            print(f"- {repo['name']}")
    
    if not repos_to_delete:
        print("No repositories to delete after applying exclusions.")
        return
    
    print("\nRepositories to delete:")
    for repo in repos_to_delete:
        print(f"- {repo['name']}")
    
    # Confirm deletion
    if not args.confirm:
        confirm = input("\nAre you sure you want to delete these repositories? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Delete repositories
    print("\nDeleting repositories...")
    success_count = 0
    for repo in repos_to_delete:
        print(f"Deleting {repo['name']}...", end="", flush=True)
        if delete_repository(repo["id"], args.project):
            print(" Success")
            success_count += 1
        else:
            print(" Failed")
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\nDeleted {success_count} out of {len(repos_to_delete)} repositories.")

if __name__ == "__main__":
    main()
