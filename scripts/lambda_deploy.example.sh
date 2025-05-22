#!/bin/bash
# lambda_deploy.example.sh
# Example deployment script for FAF
# Copy this file to lambda_deploy.sh and fill in your own values
#
# Path to your custom rules file (update this to your actual path)
FAF_CUSTOM_RULES_FILE="/path/to/your/faf_custom_rules.md"

# Remove any existing deployment package and package directory
rm -f deployment_package.zip
rm -rf package

# Generate a random name for the temporary virtual environment
ENV_NAME=$(mktemp -d -t venv-XXXXX)

# Create a virtual environment using virtualenv
virtualenv $ENV_NAME

# Activate the virtual environment
source $ENV_NAME/bin/activate

# Install dependencies in the local 'package' directory
pip install -r requirements.txt -t package

# Copy necessary files to the 'package' directory
if [ -f "$FAF_CUSTOM_RULES_FILE" ]; then
  cp "$FAF_CUSTOM_RULES_FILE" package
else
  echo "Warning: Custom rules file not found at $FAF_CUSTOM_RULES_FILE. Skipping copy."
fi
cp -r src/faf/*.py package

# Change directory to 'package' and create a ZIP archive
cd package || { echo "Error: Failed to change to package directory"; exit 1; }
zip -r ../deployment_package.zip .

# Return to the parent directory and run AWS SAM commands
cd ..
sam build || { echo "Error: SAM build failed"; exit 1; }
sam deploy || { echo "Error: SAM deploy failed"; exit 1; }

# Deactivate the virtual environment
deactivate

# Clean up the 'package' directory and the virtual environment
rm -rf package
rm -rf $ENV_NAME 