# Deployment peek challenge
Welcome to the automated provisioning documentation. Here you can find all details for running the application locally and the technical explanation about it.

## 1. Prerequisites
This environment relies on standard DevOps tooling. Ensure the following binaries are installed and accessible within your system's `$PATH`. 

**Application Runtimes & Package Managers:**
* **Python:** (v3.9) - [Install Python](https://www.python.org/downloads/)
* **Node.js:** (Node.js v22.20.0) -  [Install Node.js](https://nodejs.org/)
* **npm:** (v10.9.3) -  [Install npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* **pip:** (v24.x) -  [Install pip](https://pip.pypa.io/en/stable/installation/)

**Container Runtime & Orchestration:**
* **Docker Engine:** (v29.4.0 or higher) - [Install Docker](https://docs.docker.com/get-docker/)
* **Minikube:** (v1.35.0) - [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
* **kubectl:** (v1.32.0 or higher) - [Install kubectl](https://kubernetes.io/docs/tasks/tools/)

**Infrastructure as Code (IaC) & Configuration:**
* **Terraform:** (v1.10.5 or higher) - [Install Terraform](https://developer.hashicorp.com/terraform/downloads)
* **Helm:** (v3.12.0 or higher) -  [Install Helm](https://helm.sh/docs/intro/install/)

## 2. Architecture & Topology Overview

This environment is designed around Cloud-Native, N-Tier architecture principles. The topology ensures a clear separation of concerns between routing, compute, state management, and configuration distribution. 

Below is the logical flow of the infrastructure and how the deployed components interact:

* **Ingress Controller:** External traffic is captured by the Minikube NGINX Ingress Controller. It acts as the API Gateway, handling host-based routing and abstracting the underlying node ports.

* **Reverse Proxy:** Traffic is routed to an NGINX service, which serves as the frontend or reverse proxy. This ensures that only sanitized, HTTP-compliant traffic reaches the application backend, providing a layer of security and static asset caching.

* **Stateless Deployments:** The core application logic is deployed as stateless Kubernetes `deployments`. This ensures that pods are ephemeral and can be destroyed or recreated without data loss.

* **Horizontal Pod Autoscaling (HPA):** To guarantee high availability and resource efficiency, an HPA is configured. It monitors metric utilization (such as CPU or Memory) and dynamically scales the deployment replicas up or down to handle simulated traffic spikes, ensuring the application remains responsive under load.

* **ClusterIP Services:** All internal communication is abstracted via Kubernetes `services`. This provides stable internal DNS records and automatic load balancing across the available pod replicas, abstracting the ephemeral nature of individual pod IPs.

* **Stateful Tier:** The application state is decoupled from the compute tier and maintained in a dedicated Database deployment. *(Note: For a true production environment, this would utilize StatefulSets with Persistent Volume Claims (PVCs) or a managed DBaaS).*

* **Packaging & Templating:** The entire application stack is packaged using **Helm**. This allows for dynamic value injection making the architecture highly modular and ready to be promoted across different environments with zero code changes to the base manifests.

## 3. Deployment Instructions
The entire infrastructure and application stack provisioning has been fully automated via the `deployment.sh` script. To ensure a clean, reproducible, and error-free local environment, this script orchestrates the deployment pipeline across three distinct operational phases:

1. **Platform Bootstrapping:** Initializes the local Kubernetes environment by spinning up the Minikube cluster and configuring the appropriate local context.
2. **Build & Containerization:** Compiles the application source code and builds the required Docker images, automatically loading them into Minikube's local container registry.
3. **IaC & Application Deployment:** Executes Terraform to initialize and apply the infrastructure state. Terraform then leverages the Helm provider to seamlessly deploy the application components and routing configurations into the cluster.
4. **Exposing:** Configures access to the application updating the hosts file in your local machine, it makes the app reachable via the specified domain. It might ask for Administrator privileges. Once it's running, leave the terminal window open.

### Execution

To launch the environment, ensure the shell scripts possess the correct execution permissions and run the deployment pipeline from the `deployment/` directory:

```bash
# 1. Grant execution permissions to the operational scripts
chmod +x deployment.sh teardown.sh

# 2. Execute the automated deployment pipeline
./deployment.sh
```


You can now access the application via:

http://peek-challenge.local 

## 4. Validation & Application Access

To ensure cross-platform compatibility (especially for environments utilizing Docker Desktop or WSL2), the domain resolution is standardized to your local loopback address. 

*(Note: The deployment script attempts to automate this mapping, but manual verification is recommended).*

Ensure your system's `hosts` file (`/etc/hosts` on Unix or `C:\Windows\System32\drivers\etc\hosts` on Windows) contains the following entry:
```plaintext
127.0.0.1  peek-challenge.local
```

And then, please use one of the following methods to access the application:

**Option A:** Native Ingress via Minikube Tunnel (Recommended)
This method leverages the deployed NGINX Ingress Controller to accurately simulate production Layer 7 routing.

Open a new terminal session and execute the following command (keep this process running):

```bash
minikube tunnel
```
Open your browser and navigate seamlessly to:

http://peek-challenge.local

**Option B:** Direct Port-Forwarding (Debugging / Fallback)
If you encounter strict VM network isolation issues or prefer to bypass the Minikube Ingress routing entirely, you can establish a direct, secure tunnel to the NGINX service.

Open a new terminal session and execute the following command (keep this process running):

```bash
kubectl port-forward svc/nginx 80:80
```
You can now access the application via:

http://peek-challenge.local (or simply via http://localhost).

## 5. Teardown
You can execute the `teardown.sh` script. This process ensures the graceful destruction of the Terraform state, completely halts and deletes the Minikube cluster, and purges any localized Docker artifacts or persistent volumes generated during the build phase.

### Execution

```bash
# Execute the automated teardown pipeline
./teardown.sh
```

## 6. Production Recommendations & Trade-offs

This repository provides a fully functional local development environment. However, operating this stack securely and reliably at scale requires specific architectural shifts. If deploying to a production Tier-1 environment, I recommend the following operational upgrades:

* **Observability & Event-Driven Automation:** I recommend deploying the kube-prometheus-stack (Prometheus, Grafana, Alertmanager) to establish a baseline for observability.

* **Elasticity & Autoscaling (HPA / Cluster Autoscaler):** For production, I recommend implementing Horizontal Pod Autoscaling (HPA) to dynamically scale the application pods in response to traffic spikes. 

* **Event-Driven Automation:** To achieve traffic-based automation, the standard HPA should be augmented with Kubernetes Event-driven Autoscaling that allows the application to scale preemptively based on real-time external event metrics rather than lagging behind standard CPU/Memory thresholds.

* **State Management & Data Persistence:** For it would utilize StatefulSets paired with Persistent Volume Claims (PVCs) to ensure stable network identities and durable storage. Alternatively, offloading state management entirely to a managed DBaaS (e.g., AWS RDS or Cloud SQL) is highly recommended to simplify backups, patching, and automated failover.