#!/bin/bash -e
KEY="Project"
VALUE="trainpipe"

# NOTE!!!: this returns deleted resources too! I know that this is ridiculous but that's just the way it is.
# aws resourcegroupstaggingapi get-resources --tag-filters Key="$KEY",Values="$VALUE"

aws sqs list-queues
aws batch list-scheduling-policies
aws batch describe-job-queues
aws batch describe-job-definitions --status ACTIVE
aws batch describe-compute-environments

# aws efs describe-file-systems --tag-filters Key="$KEY",Values="$VALUE"
aws efs describe-file-systems | jq '.FileSystems[] | select(.Tags[] | .Key == "$KEY" and .Value == "$VALUE")'
aws efs describe-file-systems --query 'FileSystems[?Tags[?Key=="$KEY" && Value=="$VALUE"]]'
aws iam list-roles | grep trainpipe
