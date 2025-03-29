#!/usr/bin/env python
"""
Script to delete all pipelines and their runs in an Azure DevOps project using the Azure CLI.
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

def list_pipelines(project):
    """List all pipelines in the specified project using Azure CLI."""
    try:
        print(f"Fetching pipelines from project '{project}'...")
        result = subprocess.run(
            ['az', 'pipelines', 'list', '--project', project, '--output', 'json'],
            capture_output=True, text=True, check=True
        )
        
        pipelines = json.loads(result.stdout)
        return pipelines
    except subprocess.CalledProcessError as e:
        print(f"Error listing pipelines: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def list_pipeline_runs(pipeline_id, project):
    """List all runs for a specific pipeline."""
    try:
        result = subprocess.run(
            ['az', 'pipelines', 'runs', 'list', '--pipeline-id', str(pipeline_id), 
             '--project', project, '--output', 'json'],
            capture_output=True, text=True, check=True
        )
        
        runs = json.loads(result.stdout)
        return runs
    except subprocess.CalledProcessError as e:
        print(f"Error listing pipeline runs: {e}")
        print(f"Error output: {e.stderr}")
        return []

def delete_pipeline_run(run_id, project):
    """Delete a specific pipeline run by ID."""
    try:
        # Check the available commands in az pipelines runs
        help_result = subprocess.run(
            ['az', 'pipelines', 'runs', '--help'],
            capture_output=True, text=True
        )
        
        # The correct command is 'az pipelines run cancel'
        result = subprocess.run(
            ['az', 'pipelines', 'runs', 'cancel', '--id', str(run_id), 
             '--project', project, '--yes'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception during pipeline run cancellation: {e}")
        return False

def delete_pipeline(pipeline_id, project):
    """Delete a specific pipeline by ID."""
    try:
        result = subprocess.run(
            ['az', 'pipelines', 'delete', '--id', str(pipeline_id), 
             '--project', project, '--yes'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception during pipeline deletion: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Delete all pipelines and their runs in an Azure DevOps project")
    parser.add_argument("--organization", "-o", required=True, help="Azure DevOps organization name")
    parser.add_argument("--project", "-p", required=True, help="Azure DevOps project name")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt and delete all pipelines")
    parser.add_argument("--exclude", "-e", nargs="+", help="List of pipeline names to exclude from deletion")
    parser.add_argument("--runs-only", action="store_true", help="Delete only pipeline runs, keep the pipelines")
    
    args = parser.parse_args()
    
    # Ensure Azure DevOps CLI extension is installed
    ensure_devops_extension()
    
    # Configure default organization
    configure_devops_defaults(args.organization)
    
    # Get list of pipelines
    pipelines = list_pipelines(args.project)
    
    if not pipelines:
        print("No pipelines found in the project.")
        return
    
    exclude_list = args.exclude or []
    pipelines_to_process = [pipeline for pipeline in pipelines if pipeline["name"] not in exclude_list]
    excluded_pipelines = [pipeline for pipeline in pipelines if pipeline["name"] in exclude_list]
    
    print(f"Found {len(pipelines)} pipelines in the project.")
    print(f"{len(pipelines_to_process)} will be processed.")
    
    if excluded_pipelines:
        print("Excluded pipelines:")
        for pipeline in excluded_pipelines:
            print(f"- {pipeline['name']}")
    
    if not pipelines_to_process:
        print("No pipelines to process after applying exclusions.")
        return
    
    print("\nPipelines to process:")
    for pipeline in pipelines_to_process:
        print(f"- {pipeline['name']} (ID: {pipeline['id']})")
    
    action_desc = "cancel in-progress pipeline runs" if args.runs_only else "cancel any in-progress pipeline runs and delete the pipelines themselves"
    
    # Confirm deletion
    if not args.confirm:
        confirm = input(f"\nAre you sure you want to {action_desc}? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Process pipelines
    print("\nProcessing pipelines...")
    pipeline_success_count = 0
    run_success_count = 0
    total_runs = 0
    
    for pipeline in pipelines_to_process:
        print(f"\nProcessing pipeline: {pipeline['name']} (ID: {pipeline['id']})")
        
        # Get and cancel all runs for this pipeline
        runs = list_pipeline_runs(pipeline['id'], args.project)
        if runs:
            print(f"  Found {len(runs)} run(s) for this pipeline.")
            total_runs += len(runs)
            
            for run in runs:
                # Only try to cancel runs that are in progress
                if run.get('state') in ['inProgress', 'notStarted', 'queued']:
                    print(f"  Canceling run {run['id']}...", end="", flush=True)
                    if delete_pipeline_run(run['id'], args.project):
                        print(" Success")
                        run_success_count += 1
                    else:
                        print(" Failed")
                    time.sleep(0.5)  # Small delay to avoid rate limiting
                else:
                    print(f"  Skipping run {run['id']} (already in state: {run.get('state')})")
                    # Already completed runs don't need to be canceled
        else:
            print("  No runs found for this pipeline.")
        
        # Delete the pipeline itself if not in runs-only mode
        if not args.runs_only:
            print(f"  Deleting pipeline {pipeline['name']}...", end="", flush=True)
            if delete_pipeline(pipeline['id'], args.project):
                print(" Success")
                pipeline_success_count += 1
            else:
                print(" Failed")
            time.sleep(0.5)  # Small delay to avoid rate limiting
    
    print("\nSummary:")
    print(f"- Canceled {run_success_count} in-progress pipeline runs out of {total_runs} total runs")
    if not args.runs_only:
        print(f"- Deleted {pipeline_success_count} out of {len(pipelines_to_process)} pipelines")

if __name__ == "__main__":
    main()
