#!/bin/bash -e

# This script deletes all of the images from a certain ECR repository.

repository_name="trainpipe"

# List all image digests
images=$(aws ecr list-images --repository-name $repository_name --query 'imageIds[*].imageDigest' --output text)

# Loop through and delete each image
for image in $images
do
  aws ecr batch-delete-image --repository-name $repository_name --image-ids imageDigest=$image
done
