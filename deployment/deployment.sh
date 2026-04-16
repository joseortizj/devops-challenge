#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
REQUIRED_COMMANDS=("minikube" "docker" "terraform" "pip" "npm")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed. Please install it before running this script."
        exit 1
    fi
done

echo "====================================================="
echo "Starting platform process..."
echo "====================================================="
cd ..
pwd
ls -lha
# Check if Minikube is running
if ! minikube status >/dev/null 2>&1; then
    echo "Starting Minikube..."
    minikube start --driver=docker
else
    echo "Minikube is already running."
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows (Git Bash). Binding Docker daemon..."
    eval $(minikube -p minikube docker-env --shell=bash)
else
    echo "Setting up Minikube Docker environment for Linux/macOS..."
    eval $(minikube docker-env)
fi

minikube addons enable ingress
echo "====================================================="
echo "Platform process completed successfully."
echo "====================================================="
echo "Building and pushing Docker images..."
echo "Building votes-api image..."
cd votes-api
ls -lha
pip install -r requirements.txt
docker build -t votes-api:latest .
cd ..
cd votes-ui
echo "Building votes-ui image..."
ls -lha
npm ci
docker build -t votes-ui:latest .
cd ..
cd nginx
ls -lha
docker build -t nginx:latest .
cd ..
docker image ls
echo "====================================================="
echo "Docker images built successfully."
echo "====================================================="
echo "Deploying application to Kubernetes cluster..."
cd deployment/terraform
echo "Initializing Terraform..."
terraform init
echo "Terraform already initialized."
terraform plan
terraform apply -auto-approve
cd ..
echo "Application deployed successfully."
MINIKUBE_IP=127.0.0.1
echo "====================================================="
echo " Deployment Successful!"
echo "====================================================="
echo ""
echo "To access the application with a clean domain name, please"
echo "map the Minikube IP to our custom local domain."
echo ""
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Update the hosts file for Windows:"
    powershell.exe -NoProfile -Command "Start-Process powershell -ArgumentList '-NoProfile -Command \"Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value ''$HOST_IP peek-challenge.local''\"' -Verb RunAs"
else
    echo "Update the hosts file for macOS /  Linux :"
    echo $MINIKUBE_IP peek-challenge.local | sudo tee -a /etc/hosts
fi

echo ""
echo "You can view the application at:"
echo " http://peek-challenge.local"
echo "====================================================="
echo "Starting Minikube tunnel to expose the application... Keep this window open to maintain the tunnel."
minikube tunnel