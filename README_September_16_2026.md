# CAN-to-Cloud Analytics Platform

## Work Completed on September 16, 2026

This document records the CI/CD implementation completed on September 16, 2026 for the CAN-to-Cloud Analytics Platform.

The main objective was to automate application testing, Docker image creation, loading images into Minikube, Kubernetes deployment, and rollout verification using GitHub Actions with a self-hosted runner running inside WSL.

---

## 1. Project Outcome

The project progressed from a manual deployment process to an automated local CI/CD workflow.

### Before automation

```text
Change application code
        ↓
Run tests manually
        ↓
Build Docker images manually
        ↓
Load images into Minikube manually
        ↓
Apply Kubernetes YAML files manually
        ↓
Restart deployments manually
        ↓
Check dashboard and monitoring manually
```

### After September 16 implementation

```text
Developer changes code in WSL
        ↓
Git commit and push to main
        ↓
GitHub Actions workflow starts
        ↓
Self-hosted runner in WSL receives the job
        ↓
Python unit tests run
        ↓
Kubernetes YAML files are validated
        ↓
Docker images are built in WSL
        ↓
Images are loaded into Minikube
        ↓
Kubernetes application manifests are applied
        ↓
Deployments are restarted or updated
        ↓
Rollout status is verified
        ↓
CAN dashboard is available in Minikube
```

The self-hosted runner allows GitHub Actions to access local Docker, Minikube, kubectl, and Helm tools installed in WSL.

---

## 2. Complete Project Flow

```text
                         GitHub Repository
                                │
                                │ push to main
                                ▼
                    GitHub Actions Workflows
                                │
                                ▼
                 Self-Hosted GitHub Runner in WSL
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
             ▼                                     ▼
      Platform Workflow                    Application Workflow
      platform.yml                         application.yml
             │                                     │
             │                                     ├─ Run tests
             │                                     ├─ Validate YAML
             │                                     ├─ Build images
             │                                     ├─ Load images
             │                                     ├─ Apply manifests
             │                                     └─ Verify rollouts
             │
             ├─ Create monitoring namespace
             ├─ Install/upgrade Prometheus stack
             ├─ Create PVC
             ├─ Deploy Redis
             └─ Apply ServiceMonitors
             │                                     │
             └──────────────────┬──────────────────┘
                                ▼
                         Minikube in WSL
                                │
       ┌────────────────────────┼─────────────────────────┐
       │                        │                         │
       ▼                        ▼                         ▼
Vehicle Data Simulator       CAN Parser             Dashboard
       │                        │                         │
       │ Generate CAN data      │ Decode messages         │ Display data
       ▼                        ▼                         ▼
                             Redis / SQLite / PVC
                                │
                                ▼
                     Prometheus and Grafana
```

---

## 3. Why Two Pipelines Were Created

The original workflow built application images and restarted existing Deployments. It assumed that Redis, PVCs, Services, ServiceMonitors, Prometheus, Grafana, and the application Deployments already existed.

That workflow could update a running environment, but it could not prepare a fresh Minikube cluster.

To solve this, the automation was separated into two workflows.

### Platform workflow

The platform workflow prepares the environment and is normally run manually or when platform configuration changes.

It manages:

- Monitoring namespace
- Prometheus and Grafana stack
- PersistentVolumeClaim
- Redis Deployment
- Redis Service
- Parser Service
- Simulator Service
- Parser ServiceMonitor
- Simulator ServiceMonitor

### Application workflow

The application workflow validates, builds, and deploys frequently changing application components.

It manages:

- Unit tests
- YAML validation
- Dashboard Docker image
- Parser Docker image
- Vehicle simulator Docker image
- Image loading into Minikube
- Kubernetes application manifests
- Deployment rollout verification

This separation follows a practical platform/application model:

```text
Platform resources
Change less frequently
Prometheus, Grafana, Redis, PVC, Services, ServiceMonitors

Application resources
Change frequently
Dashboard, Parser, Vehicle Simulator
```

---

## 4. Repository Structure

The project repository used during the implementation has the following structure:

```text
can-cloud-platform/
├── .github/
│   └── workflows/
│       ├── platform.yml
│       └── application.yml
├── dashboard/
│   ├── Dockerfile
│   ├── README.md
│   ├── app.py
│   └── requirements.txt
├── parser/
│   ├── Dockerfile
│   ├── parser.py
│   ├── requirements.txt
│   └── decoders/
├── simulator/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── deployment/
│   ├── pvc_parser.yaml
│   ├── redis_deployment.yaml
│   ├── redis_service.yaml
│   ├── dashboard_deployment.yaml
│   ├── dashboard_service.yaml
│   ├── parser_deployment.yaml
│   ├── parser_service.yaml
│   ├── vehicle_simulator_deployment.yaml
│   ├── vehicle_simulator_service.yaml
│   ├── parser_servicemonitor.yaml
│   └── vehicle_simulator_servicemonitor.yaml
├── monitoring/
├── tests/
└── README.md
```

> File names must match the actual files in the repository. If a manifest uses a different name, update the workflow path accordingly.

---

## 5. Technologies Used

- Python
- Pytest
- Docker
- Kubernetes
- Minikube
- WSL
- Git
- GitHub
- GitHub Actions
- Self-hosted GitHub Actions runner
- Helm
- Redis
- Prometheus
- Grafana
- Streamlit
- YAML and yamllint

---

# Part A: Self-Hosted Runner Setup

## 6. Why a Self-Hosted Runner Was Required

A GitHub-hosted runner cannot directly access the Minikube cluster running inside the local WSL environment.

The self-hosted runner is installed in WSL so that the workflow can use:

```text
Local source checkout
Local Docker daemon
Local Minikube cluster
Local kubectl context
Local Helm installation
```

The resulting flow is:

```text
GitHub Actions
      ↓
Self-hosted runner in WSL
      ↓
Docker build
      ↓
Minikube image load
      ↓
kubectl apply
      ↓
Kubernetes rollout
```

---

## 7. Create a Separate Runner Directory

The runner should be stored outside the project repository.

```bash
cd ~
mkdir -p github-actions-runner/actions-runner
cd github-actions-runner/actions-runner
```

Recommended layout:

```text
~/
├── github-actions-runner/
│   └── actions-runner/
│       ├── _work/
│       ├── bin/
│       ├── externals/
│       ├── run.sh
│       └── svc.sh
│
└── canlog-dashboard-live/
    └── can-cloud-platform/
```

The `_work` directory is used by GitHub Actions to check out the repository and execute workflow steps.

---

## 8. Verify WSL Prerequisites

Run these commands in WSL before starting the runner:

```bash
docker version
kubectl version --client
minikube status
helm version
```

Verify that:

- Docker is accessible.
- kubectl is installed.
- Minikube is running.
- Helm is installed.

Check the current Kubernetes context:

```bash
kubectl config current-context
```

Expected context:

```text
minikube
```

Verify cluster access:

```bash
kubectl get nodes
```

---

## 9. Configure the Runner

In GitHub, open:

```text
Repository
→ Settings
→ Actions
→ Runners
→ New self-hosted runner
→ Linux
→ x64
```

Run the installation and configuration commands displayed by GitHub inside:

```text
~/github-actions-runner/actions-runner
```

When prompted for the work folder:

```text
Enter name of work folder: [press Enter for _work]
```

Press Enter to keep the default `_work` directory.

Start the runner using either of the following methods.

### Interactive runner

```bash
./run.sh
```

This terminal must remain open while workflows are running.

### Service mode, if supported in the WSL setup

```bash
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

In GitHub, verify that the runner status is `Online`.

---

# Part B: Platform Workflow

## 10. Platform Workflow Purpose

File:

```text
.github/workflows/platform.yml
```

The platform workflow prepares a fresh Minikube environment. It is intentionally configured with `workflow_dispatch` because platform components should not be reinstalled on every application commit.

---

## 11. Example Platform Workflow

```yaml
---
name: Platform Setup

on:
  workflow_dispatch:

jobs:
  platform-setup:
    runs-on: self-hosted

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Verify Minikube
        run: |
          minikube status
          kubectl config current-context
          kubectl get nodes

      - name: Create Monitoring Namespace
        run: |
          kubectl create namespace monitoring \
            --dry-run=client \
            -o yaml | kubectl apply -f -

      - name: Add Prometheus Helm Repository
        run: |
          helm repo add prometheus-community \
            https://prometheus-community.github.io/helm-charts
          helm repo update

      - name: Install or Upgrade Prometheus Stack
        run: |
          helm upgrade --install prometheus \
            prometheus-community/kube-prometheus-stack \
            --namespace monitoring

      - name: Create Persistent Volume Claim
        run: |
          kubectl apply -f deployment/pvc_parser.yaml

      - name: Deploy Redis
        run: |
          kubectl apply -f deployment/redis_deployment.yaml
          kubectl apply -f deployment/redis_service.yaml

      - name: Apply Application Services
        run: |
          kubectl apply -f deployment/parser_service.yaml
          kubectl apply -f deployment/vehicle_simulator_service.yaml
          kubectl apply -f deployment/dashboard_service.yaml

      - name: Apply ServiceMonitors
        run: |
          kubectl apply -f deployment/parser_servicemonitor.yaml
          kubectl apply -f deployment/vehicle_simulator_servicemonitor.yaml

      - name: Verify Platform
        run: |
          kubectl get namespace monitoring
          kubectl get pods -n monitoring
          kubectl get pvc
          kubectl get svc
          kubectl get servicemonitor
```

### Important

The monitoring Helm release name in this example is `prometheus`. Therefore the commonly used services are expected to begin with `prometheus-`. Verify the exact names with:

```bash
kubectl get svc -n monitoring
```

---

# Part C: Application Workflow

## 12. Application Workflow Purpose

File:

```text
.github/workflows/application.yml
```

This workflow runs for application changes. It performs CI and local continuous delivery to Minikube.

---

## 13. Example Application Workflow

```yaml
---
name: CAN Application CI-CD

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-test-deploy:
    runs-on: self-hosted

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Test and YAML Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest yamllint

      - name: Run Unit Tests
        run: |
          pytest

      - name: Validate Kubernetes YAML
        run: |
          yamllint deployment/

      - name: Verify Local Platform
        run: |
          docker version
          minikube status
          kubectl config current-context
          kubectl get nodes

      - name: Show Repository Structure
        run: |
          pwd
          ls
          ls dashboard
          ls parser
          ls simulator

      - name: Build Dashboard Image
        run: |
          docker build -t can-dashboard:v1 ./dashboard

      - name: Build Parser Image
        run: |
          docker build -t can-parser:v1 ./parser

      - name: Build Vehicle Simulator Image
        run: |
          docker build -t vehicle_data_simulator:v1 ./simulator

      - name: Load Images into Minikube
        run: |
          minikube image load can-dashboard:v1
          minikube image load can-parser:v1
          minikube image load vehicle_data_simulator:v1

      - name: Apply Application Manifests
        run: |
          kubectl apply -f deployment/dashboard_deployment.yaml
          kubectl apply -f deployment/dashboard_service.yaml
          kubectl apply -f deployment/parser_deployment.yaml
          kubectl apply -f deployment/parser_service.yaml
          kubectl apply -f deployment/vehicle_simulator_deployment.yaml
          kubectl apply -f deployment/vehicle_simulator_service.yaml

      - name: Restart Application Deployments
        run: |
          kubectl rollout restart deployment/can-dashboard
          kubectl rollout restart deployment/can-parser
          kubectl rollout restart deployment/vehicle-data-simulator

      - name: Wait for Rollouts
        run: |
          kubectl rollout status deployment/can-dashboard --timeout=180s
          kubectl rollout status deployment/can-parser --timeout=180s
          kubectl rollout status deployment/vehicle-data-simulator --timeout=180s

      - name: Verify Application
        run: |
          kubectl get deployments
          kubectl get pods
          kubectl get svc
```

> The image name in each Deployment YAML must exactly match the image name built by the workflow.

Example:

```yaml
containers:
  - name: vehicle-data-simulator
    image: vehicle_data_simulator:v1
    imagePullPolicy: Never
```

---

## 14. Important Docker Build Path Correction

The first Docker build attempt used:

```bash
docker build -t can-dashboard:v1 .
```

That command failed because no Dockerfile existed at the repository root checked out by the runner.

The repository stores Dockerfiles inside component directories. Therefore the correct commands are:

```bash
docker build -t can-dashboard:v1 ./dashboard
docker build -t can-parser:v1 ./parser
docker build -t vehicle_data_simulator:v1 ./simulator
```

The final `./dashboard`, `./parser`, and `./simulator` arguments are the Docker build contexts.

The runner checkout path may look similar to:

```text
~/github-actions-runner/actions-runner/_work/
└── cloud-native-can-dashboard/
    └── cloud-native-can-dashboard/
```

This nested runner directory is normal. The workflow executes from the checked-out repository root.

---

## 15. YAML Validation Improvement

`yamllint` reported:

```text
1:1 [document-start] missing document start "---"
```

The preferred fix is to add a YAML document-start marker to the beginning of each YAML file:

```yaml
---
apiVersion: apps/v1
kind: Deployment
```

Apply this style to Kubernetes manifests and workflow files.

If required, a project-specific `.yamllint.yml` can be used, but keeping the document-start rule enabled provides cleaner YAML.

---

# Part D: Execution Procedure

## 16. Fresh Environment Execution Order

Use this process when Minikube is running but the project platform and applications are not deployed.

### Step 1: Start Minikube

```bash
minikube start
```

Verify:

```bash
minikube status
kubectl get nodes
kubectl config current-context
```

### Step 2: Start or verify the self-hosted runner

Interactive mode:

```bash
cd ~/github-actions-runner/actions-runner
./run.sh
```

Or verify service mode:

```bash
cd ~/github-actions-runner/actions-runner
sudo ./svc.sh status
```

Verify the runner is `Online` in GitHub.

### Step 3: Run the platform workflow

In GitHub:

```text
Repository
→ Actions
→ Platform Setup
→ Run workflow
→ Select main
→ Run workflow
```

Wait for all platform steps to complete successfully.

### Step 4: Verify platform resources in WSL

```bash
kubectl get pvc
kubectl get pods
kubectl get svc
kubectl get pods -n monitoring
kubectl get svc -n monitoring
kubectl get servicemonitor
```

Expected platform state:

```text
PVC                       Bound
Redis                     Running
Prometheus components     Running
Grafana                    Running
Services                   Created
ServiceMonitors            Created
```

### Step 5: Run the application workflow

The application workflow can start automatically after a push to `main`, or it can be started manually if `workflow_dispatch` is enabled.

To trigger it with a code change:

```bash
cd ~/canlog-dashboard-live/can-cloud-platform
git status
git add .
git commit -m "Deploy CAN application update"
git push origin main
```

GitHub Actions then performs:

```text
Checkout
→ Python setup
→ Dependency installation
→ Unit tests
→ YAML validation
→ Docker builds
→ Minikube image loading
→ Manifest application
→ Rollout restart
→ Rollout verification
```

### Step 6: Verify the application

```bash
kubectl get deployments
kubectl get pods
kubectl get svc
```

Check rollout status:

```bash
kubectl rollout status deployment/can-dashboard
kubectl rollout status deployment/can-parser
kubectl rollout status deployment/vehicle-data-simulator
```

Check logs:

```bash
kubectl logs -f deployment/can-dashboard
kubectl logs -f deployment/can-parser
kubectl logs -f deployment/vehicle-data-simulator
```

Use `Ctrl+C` to stop following logs.

---

## 17. Normal Application Update Execution

Use this shorter process when the platform is already installed and healthy.

```bash
cd ~/canlog-dashboard-live/can-cloud-platform
```

Make the required code change, then run:

```bash
git status
git add .
git commit -m "Update CAN application"
git push origin main
```

The application workflow updates:

- Dashboard
- Parser
- Vehicle simulator

The application workflow does not need to reinstall:

- Prometheus
- Grafana
- Redis
- PVC
- ServiceMonitors

Verify after the workflow succeeds:

```bash
kubectl get pods
kubectl get deployments
kubectl rollout status deployment/can-dashboard
kubectl rollout status deployment/can-parser
kubectl rollout status deployment/vehicle-data-simulator
```

---

# Part E: Dashboard and Monitoring Access

## 18. Open the CAN Dashboard

Check the dashboard service:

```bash
kubectl get svc
```

If the service is named `can-dashboard-svc`, retrieve its URL:

```bash
minikube service can-dashboard-svc --url
```

Or request Minikube to open it:

```bash
minikube service can-dashboard-svc
```

Verify the dashboard is running:

```bash
kubectl rollout status deployment/can-dashboard
kubectl logs deployment/can-dashboard
```

---

## 19. Open Prometheus

First verify the service name:

```bash
kubectl get svc -n monitoring
```

Port-forward the Prometheus service:

```bash
kubectl port-forward \
  svc/prometheus-kube-prometheus-prometheus \
  9090:9090 \
  -n monitoring
```

Open in a browser:

```text
http://localhost:9090
```

If port 9090 is already in use, identify the process:

```bash
sudo lsof -i :9090
```

Or use another local port:

```bash
kubectl port-forward \
  svc/prometheus-kube-prometheus-prometheus \
  9091:9090 \
  -n monitoring
```

Then open:

```text
http://localhost:9091
```

---

## 20. Open Grafana

Verify the service:

```bash
kubectl get svc -n monitoring
```

Port-forward Grafana:

```bash
kubectl port-forward \
  svc/prometheus-grafana \
  3000:80 \
  -n monitoring
```

Open:

```text
http://localhost:3000
```

Obtain the Grafana admin password:

```bash
kubectl get secret prometheus-grafana \
  -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 -d
```

Default user:

```text
admin
```

---

# Part F: Understanding What Runs Where

## 21. Where the Build Happens

Because the workflow uses:

```yaml
runs-on: self-hosted
```

the build runs inside the WSL environment on the local machine.

```text
GitHub receives the push
        ↓
GitHub assigns the job to the WSL runner
        ↓
Runner checks out the repository into _work
        ↓
Docker builds images using the local Docker daemon
        ↓
Images are copied into Minikube
        ↓
kubectl updates the local Minikube cluster
```

Verify locally built images:

```bash
docker images | grep -E "can-dashboard|can-parser|vehicle_data_simulator"
```

Verify images in Minikube:

```bash
minikube image ls | grep -E "can-dashboard|can-parser|vehicle_data_simulator"
```

---

## 22. Platform Pipeline Versus Application Pipeline

### Platform workflow execution

```text
Manual workflow dispatch
        ↓
Verify Minikube
        ↓
Create monitoring namespace
        ↓
Install/upgrade Prometheus stack
        ↓
Create PVC
        ↓
Deploy Redis
        ↓
Create Services
        ↓
Create ServiceMonitors
        ↓
Verify platform
```

### Application workflow execution

```text
Push or pull request to main
        ↓
Run tests
        ↓
Validate YAML
        ↓
Build application images
        ↓
Load images into Minikube
        ↓
Apply application manifests
        ↓
Restart deployments
        ↓
Wait for rollouts
        ↓
Verify pods and services
```

### Required order for a fresh cluster

```text
1. Start Minikube
2. Ensure self-hosted runner is online
3. Run platform.yml
4. Verify platform resources
5. Run application.yml
6. Verify application rollouts
7. Open dashboard
8. Open Prometheus and Grafana if required
```

### Required order for a normal code update

```text
1. Ensure Minikube is running
2. Ensure the self-hosted runner is online
3. Commit and push the application change
4. application.yml runs automatically
5. Verify rollouts and dashboard
```

---

# Part G: Troubleshooting Guide

## 23. Dockerfile Not Found

### Error

```text
unable to evaluate symlinks in Dockerfile path
Dockerfile: no such file or directory
```

### Cause

The workflow used the repository root as the Docker build context, but the Dockerfiles are stored inside component directories.

### Fix

```bash
docker build -t can-dashboard:v1 ./dashboard
docker build -t can-parser:v1 ./parser
docker build -t vehicle_data_simulator:v1 ./simulator
```

Verify the files before building:

```bash
ls dashboard/Dockerfile
ls parser/Dockerfile
ls simulator/Dockerfile
```

---

## 24. Image Name Mismatch

The image name used in all three locations must match:

1. `docker build`
2. `minikube image load`
3. Kubernetes Deployment YAML

Correct example:

```text
Build:       vehicle_data_simulator:v1
Load:        vehicle_data_simulator:v1
Deployment:  vehicle_data_simulator:v1
```

Check the Deployment image:

```bash
kubectl get deployment vehicle-data-simulator \
  -o jsonpath="{.spec.template.spec.containers[0].image}"
```

---

## 25. Deployment Not Found During Rollout Restart

### Error

```text
Error from server (NotFound): deployments.apps "can-dashboard" not found
```

### Cause

The workflow attempted `kubectl rollout restart` before creating the Deployment.

### Fix

Apply the manifest before restarting:

```bash
kubectl apply -f deployment/dashboard_deployment.yaml
kubectl rollout restart deployment/can-dashboard
```

The application workflow in this README applies manifests before rollout verification, allowing it to work with a freshly prepared platform.

---

## 26. Minikube Is Running but Nothing Is Deployed

If only Minikube is running, an update-only workflow will fail because the target Deployments do not exist.

Use this order:

```text
Run platform.yml
        ↓
Run application.yml
```

Verify resources:

```bash
kubectl get all
kubectl get pvc
kubectl get servicemonitor
kubectl get all -n monitoring
```

---

## 27. YAML Document Start Warning

### Warning

```text
1:1 [document-start] missing document start "---"
```

### Fix

Add this as the first line of the YAML file:

```yaml
---
```

Then validate locally:

```bash
yamllint deployment/
yamllint .github/workflows/
```

---

## 28. Docker Legacy Builder Warning

A Docker build may display a warning that the legacy builder is deprecated. This warning is separate from a missing Dockerfile error.

Check whether Buildx is available:

```bash
docker buildx version
```

If Buildx is available, the existing `docker build` commands can continue to use the Docker BuildKit integration provided by the local Docker installation.

The critical September 16 build failure was corrected by using the proper component build contexts.

---

## 29. Runner Offline

Check in GitHub:

```text
Repository
→ Settings
→ Actions
→ Runners
```

If the runner is offline, start it from WSL:

```bash
cd ~/github-actions-runner/actions-runner
./run.sh
```

Or, when configured as a service:

```bash
sudo ./svc.sh status
sudo ./svc.sh start
```

---

## 30. Minikube Is Not Accessible from the Workflow

Add or run these checks:

```bash
minikube status
kubectl config current-context
kubectl get nodes
```

Expected context:

```text
minikube
```

The commands must succeed under the same WSL user account that runs the self-hosted runner.

---

## 31. Dashboard Cannot Be Opened

Check resources:

```bash
kubectl get pods
kubectl get svc
kubectl get endpoints can-dashboard-svc
```

Check logs:

```bash
kubectl logs deployment/can-dashboard
```

Get the dashboard URL:

```bash
minikube service can-dashboard-svc --url
```

---

## 32. Monitoring Components Are Missing

The application workflow does not install Prometheus and Grafana.

Run the platform workflow, then verify:

```bash
helm list -n monitoring
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

---

# Part H: Verification Checklist

## 33. Self-Hosted Runner

- [ ] Runner directory is outside the source repository.
- [ ] Runner appears Online in GitHub.
- [ ] Docker is accessible from the runner user.
- [ ] kubectl uses the Minikube context.
- [ ] Helm is available.

## 34. Platform Workflow

- [ ] Platform workflow completed successfully.
- [ ] Monitoring namespace exists.
- [ ] Prometheus pods are Running.
- [ ] Grafana pod is Running.
- [ ] PVC status is Bound.
- [ ] Redis pod is Running.
- [ ] Redis Service exists.
- [ ] Parser and simulator Services exist.
- [ ] ServiceMonitors exist.

## 35. Application Workflow

- [ ] Unit tests passed.
- [ ] YAML validation passed.
- [ ] Dashboard image built.
- [ ] Parser image built.
- [ ] Simulator image built.
- [ ] Images loaded into Minikube.
- [ ] Application manifests applied.
- [ ] Dashboard rollout succeeded.
- [ ] Parser rollout succeeded.
- [ ] Simulator rollout succeeded.
- [ ] Dashboard is reachable.

## 36. Useful Verification Commands

```bash
minikube status
kubectl get nodes
kubectl get deployments
kubectl get pods
kubectl get svc
kubectl get pvc
kubectl get servicemonitor
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

Check application logs:

```bash
kubectl logs deployment/can-dashboard --tail=100
kubectl logs deployment/can-parser --tail=100
kubectl logs deployment/vehicle-data-simulator --tail=100
```

Check rollout history:

```bash
kubectl rollout history deployment/can-dashboard
kubectl rollout history deployment/can-parser
kubectl rollout history deployment/vehicle-data-simulator
```

---

# Part I: Summary of September 16 Achievement

On September 16, 2026, the CAN-to-Cloud Analytics Platform achieved the following practical milestones:

- Configured a GitHub Actions self-hosted runner in WSL.
- Confirmed that workflow jobs execute on the local WSL machine.
- Connected the runner to local Docker, Minikube, kubectl, and Helm.
- Added automated Python test execution.
- Added Kubernetes YAML validation.
- Corrected Docker build contexts for component-level Dockerfiles.
- Automated Docker image builds for dashboard, parser, and simulator.
- Automated image loading into Minikube.
- Automated application Deployment updates and rollout checks.
- Confirmed a successful GitHub Actions job.
- Clarified that an update-only workflow requires pre-existing Deployments.
- Separated platform provisioning from application delivery.
- Defined a platform workflow for Redis, PVC, monitoring, Services, and ServiceMonitors.
- Defined an application workflow for tests, builds, image loading, manifest application, and rollouts.
- Documented the correct sequence for fresh setup and normal application updates.

The final local delivery model is:

```text
Git Push
    ↓
GitHub Actions
    ↓
Self-Hosted Runner in WSL
    ↓
Tests and YAML validation
    ↓
Docker image builds
    ↓
Minikube image load
    ↓
Kubernetes deployment
    ↓
Rollout verification
    ↓
CAN dashboard, Prometheus and Grafana
```

---

## Author

**Reena Jadhav**  
Product and Manufacturing Test Engineering Specialist  
CAN | Python | Docker | Kubernetes | Minikube | CI/CD | Prometheus | Grafana

---

## Note

This README documents the implementation and troubleshooting work performed on September 16, 2026. Workflow and Kubernetes manifest file names should be aligned with the actual repository before execution.
