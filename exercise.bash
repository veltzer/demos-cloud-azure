#!/bin/bash -ex

# parameters
export PERSONAL_ACCESS_TOKEN
PERSONAL_ACCESS_TOKEN=$(cat ~/.token)
export REPO_NAME="new_repo10"
export ORGANIZATION="markveltzer"
export PROJECT="training"

# code
az devops configure --defaults organization="https://dev.azure.com/${ORGANIZATION}" project="${PROJECT}"
EXISTING_REPO=$(az repos list --query "[?name=='${REPO_NAME}'].name" -o tsv)
if [ -z "${EXISTING_REPO}" ]
then
	echo "Creating repository ${REPO_NAME}"
	az repos create --name "${REPO_NAME}" > /dev/null
else
	echo "Repository [${REPO_NAME}] already exists."
fi
REPO_URL="https://${PERSONAL_ACCESS_TOKEN}@dev.azure.com/markveltzer/training/_git/${REPO_NAME}"

cd project
rm -rf .git
git init
# git remote remove origin 2>/dev/null
git remote add origin "${REPO_URL}"
# git pull origin master --rebase
git add .
git commit -m "first commit of all files"
git push -u origin master
echo "push ok"
cd ..
