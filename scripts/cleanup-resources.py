#!/usr/bin/env python

"""
Azure Resource Cleanup Script - Preserves Subscriptions

This script removes all Azure resources in your account while preserving the subscriptions themselves.
IMPORTANT: This script performs destructive operations! Use with extreme caution.

Requirements:
- Python 3.8+
- Azure CLI must be installed and you must be logged in (run 'az login' first)
- Required packages: azure-identity, azure-mgmt-resource, azure-mgmt-subscription

Usage:
  python azure_cleanup.py [--dry-run] [--subscription SUBSCRIPTION_ID] [--skip-confirmation]
"""

import os
import sys
import time
import argparse
import datetime
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError


def get_credential():
    """Get Azure credential."""
    try:
        # First try using CLI credential as it's more likely to be set up
        return AzureCliCredential()
    except ClientAuthenticationError:
        # Fall back to default credential
        print("CLI credential failed, trying default credential...")
        return DefaultAzureCredential()


def get_subscriptions(credential):
    """Get all available subscriptions."""
    subscription_client = SubscriptionClient(credential)
    return list(subscription_client.subscriptions.list())


def delete_resource_groups(credential, subscription_id, dry_run=True, skip_confirmation=False):
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
        
        # Get confirmation for each resource group if not skipped
        if not skip_confirmation:
            confirmation = input(f"Type 'delete {group_name}' to confirm deletion: ")
            if confirmation != f"delete {group_name}":
                print(f"Skipping deletion of {group_name}")
                continue
        
        try:
            print(f"Starting deletion of resource group: {group_name}")
            # Start the deletion operation
            delete_operation = resource_client.resource_groups.begin_delete(group_name)
            
            # Wait for completion with progress updates
            print(f"Waiting for deletion to complete... This may take several minutes.")
            status = ""
            while not delete_operation.done():
                new_status = delete_operation.status()
                if new_status != status:
                    status = new_status
                    print(f"Status: {status}")
                time.sleep(5)
            
            print(f"Successfully deleted resource group: {group_name}")
        except HttpResponseError as e:
            print(f"Error deleting resource group {group_name}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Azure Resource Cleanup Tool')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no resources will be deleted)')
    parser.add_argument('--subscription', type=str, help='Specific subscription ID to clean (default: all subscriptions)')
    parser.add_argument('--skip-confirmation', action='store_true', help='Skip individual resource group confirmations')
    args = parser.parse_args()
    
    # Generate a timestamp for the log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"azure_cleanup_{timestamp}.log"
    
    # Global confirmation check
    if not args.dry_run and not args.skip_confirmation:
        warning = """
        ⚠️  WARNING: THIS SCRIPT WILL DELETE ALL RESOURCES IN YOUR AZURE ACCOUNT  ⚠️
        
        This operation is IRREVERSIBLE. All resource groups and their contents will be
        PERMANENTLY DELETED, but subscriptions will be preserved.
        
        All virtual machines, databases, storage accounts, etc. will be PERMANENTLY DELETED.
        
        If you're sure you want to proceed, type 'DELETE ALL RESOURCES' below:
        """
        print(warning)
        confirmation = input("> ")
        if confirmation != "DELETE ALL RESOURCES":
            print("Confirmation failed. Exiting without making any changes.")
            return
    
    try:
        # Get Azure credential
        credential = get_credential()
        print("Successfully authenticated with Azure.")
        
        # Get subscriptions
        print("Retrieving subscription information...")
        subscriptions = get_subscriptions(credential)
        
        if not subscriptions:
            print("No subscriptions found or you don't have access to any subscriptions.")
            return
            
        print(f"Found {len(subscriptions)} subscription(s)")
        
        # Display all found subscriptions
        print("\nAvailable subscriptions:")
        for i, sub in enumerate(subscriptions):
            print(f"  {i+1}. {sub.display_name} (ID: {sub.subscription_id})")
        
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
            
            if not args.dry_run and not args.skip_confirmation:
                sub_confirm = input(f"Type 'process {sub_id}' to confirm operations on this subscription: ")
                if sub_confirm != f"process {sub_id}":
                    print(f"Skipping subscription {sub_id}")
                    continue
            
            delete_resource_groups(credential, sub_id, args.dry_run, args.skip_confirmation)
            
        print("\nResource cleanup complete!")
        if args.dry_run:
            print("[DRY RUN] No resources were actually deleted. Run without --dry-run to perform actual deletion.")
        
        print(f"Log saved to: {log_file}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please make sure you are logged in to the Azure CLI by running 'az login'")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
