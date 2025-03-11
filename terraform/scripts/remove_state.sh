#!/bin/bash -e
aws s3api delete-object --bucket "sagemaker-tf-backend" --key "trainpipe"
