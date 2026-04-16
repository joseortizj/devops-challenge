#!/bin/bash
echo "======================================================================="
echo "Cleaning up resources..."
cd terraform
terraform destroy -auto-approve
cd ..
minikube stop
minikube delete --all
echo "Resources cleaned up successfully."
echo "======================================================================="