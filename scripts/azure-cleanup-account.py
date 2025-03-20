#!/usr/bin/env python

"""
Azure Account Resource Cleanup Script

This script deletes resources from an Azure account. 
USE WITH EXTREME CAUTION - This script will delete ALL resources in the specified subscriptions!

Requirements:
- Python 3.8+
- Azure SDK libraries (azure-identity, azure-mgmt-resource, azure-mgmt-compute, etc.)
- Appropriate permissions in your Azure account

Installation:
pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-network azure-mgmt-storage azure-mgmt-web

Before running:
1. Log in using Azure CLI: az login
2. Review the script carefully and understand what it will delete
3. Add any confirmation checks or resource filters you need
4. Consider running with --dry-run first to see what would be deleted
"""

import os
import time
import argparse
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.core.exceptions import HttpResponseError


def get_subscriptions(credential):
    """Get all available subscriptions."""
    subscription_client = SubscriptionClient(credential)
    return list(subscription_client.subscriptions.list())


def delete_resource_groups(credential, subscription_id, dry_run=True):
    """Delete all resource groups in a subscription."""
    resource_client = ResourceManagementClient(credential, subscription_id)
    
    # Get all resource groups
    resource_groups = list(resource_client.resource_groups.list())
    print(f"Found {len(resource_groups)} resource groups in subscription {subscription_id}")
    
    for group in resource_groups:
        group_name = group.name
        print(f"Preparing to delete resource group: {group_name}")
        
        if dry_run:
            print(f"[DRY RUN] Would delete resource group: {group_name}")
            continue
            
        # Get confirmation for each resource group
        confirmation = input(f"Type 'delete {group_name}' to confirm deletion: ")
        if confirmation != f"delete {group_name}":
            print(f"Skipping deletion of {group_name}")
            continue
            
        try:
            print(f"Starting deletion of resource group: {group_name}")
            # Start the deletion operation (this returns a long-running operation)
            delete_operation = resource_client.resource_groups.begin_delete(group_name)
            
            # Wait for the operation to complete
            print(f"Waiting for deletion to complete... This may take several minutes.")
            delete_operation.wait()
            
            print(f"Successfully deleted resource group: {group_name}")
        except HttpResponseError as e:
            print(f"Error deleting resource group {group_name}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Azure Resource Cleanup Tool')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no resources will be deleted)')
    parser.add_argument('--subscription', type=str, help='Specific subscription ID to clean (default: all subscriptions)')
    parser.add_argument('--force', action='store_true', help='Skip individual resource group confirmations')
    args = parser.parse_args()
    
    # Global confirmation check
    if not args.dry_run:
        warning = """
        ⚠️  WARNING: THIS SCRIPT WILL DELETE ALL RESOURCES IN YOUR AZURE ACCOUNT  ⚠️
        
        This operation is IRREVERSIBLE and will delete ALL resources in the selected subscriptions.
        All virtual machines, databases, storage accounts, and other resources will be PERMANENTLY DELETED.
        
        If you're sure you want to proceed, type 'I UNDERSTAND THE CONSEQUENCES' below:
        """
        print(warning)
        confirmation = input("> ")
        if confirmation != "I UNDERSTAND THE CONSEQUENCES":
            print("Confirmation failed. Exiting without making any changes.")
            return
    
    # Get credentials and subscriptions
    try:
        credential = DefaultAzureCredential()
        subscriptions = get_subscriptions(credential)
        
        if not subscriptions:
            print("No subscriptions found or you don't have access to any subscriptions.")
            return
            
        print(f"Found {len(subscriptions)} subscription(s)")
        
        # Filter to specific subscription if provided
        if args.subscription:
            subscriptions = [s for s in subscriptions if s.subscription_id == args.subscription]
            if not subscriptions:
                print(f"No subscription found with ID: {args.subscription}")
                return
        
        # Process each subscription
        for subscription in subscriptions:
            sub_id = subscription.subscription_id
            sub_name = subscription.display_name
            print(f"\nProcessing subscription: {sub_name} ({sub_id})")
            
            if not args.dry_run:
                sub_confirm = input(f"Type 'process {sub_id}' to confirm operations on this subscription: ")
                if sub_confirm != f"process {sub_id}":
                    print(f"Skipping subscription {sub_id}")
                    continue
            
            delete_resource_groups(credential, sub_id, args.dry_run)
            
        print("\nResource cleanup complete!")
        if args.dry_run:
            print("[DRY RUN] No resources were actually deleted. Run without --dry-run to perform actual deletion.")
            
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
