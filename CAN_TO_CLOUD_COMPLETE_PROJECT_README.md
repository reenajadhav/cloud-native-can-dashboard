# CAN-to-Cloud Analytics Platform

Complete cloud-native project README for local setup, application execution, CI/CD, GitOps deployment, observability, validation, promotion, rollback, and troubleshooting.

> Current example image tag: `44`. Replace it with the active CI build number when required.

---

## 1. Project objective

The CAN-to-Cloud Analytics Platform is an automotive telemetry proof of concept that demonstrates a complete cloud-native delivery and runtime flow:

```text
Vehicle Simulator
      |
      | Raw CAN frames
      v
Redis Queue
      |
      | Buffered messages
      v
CAN Parser
      |
      | Decoded signals
      v
SQLite on Kubernetes PVC
      |
      v
Streamlit Dashboard

Simulator + Parser metrics
      |
      v
Prometheus -> Grafana
```

The project combines automotive CAN knowledge with Python, Redis, SQLite, Streamlit, Docker, Kubernetes, Helm, GitHub Actions, Argo CD, Prometheus, and Grafana.

---

## 2. What each component does

| Component | Definition | Responsibility |
|---|---|---|
| Vehicle simulator | Python telemetry producer | Generates realistic CAN frames and publishes them to Redis |
| Redis | In-memory message queue | Decouples the simulator from the parser and buffers messages |
| Parser | Python telemetry consumer | Reads raw frames, identifies CAN IDs, decodes payloads, and writes engineering signals |
| SQLite | Lightweight relational database | Stores decoded signal records on persistent storage |
| PVC | Kubernetes PersistentVolumeClaim | Keeps SQLite data available across pod restarts |
| Streamlit dashboard | Browser-based UI | Displays latest signal values, trends, timestamps, CAN IDs, and units |
| Docker | Container runtime/package format | Packages simulator, parser, and dashboard independently |
| Kubernetes | Container orchestrator | Runs, restarts, networks, and manages application workloads |
| Helm | Kubernetes package manager | Templates manifests and provides environment-specific values |
| GitHub Actions | CI/CD automation | Tests, builds, tags, promotes, and updates GitOps configuration |
| Argo CD | GitOps continuous delivery controller | Reconciles the cluster with the desired state stored in Git |
| Prometheus | Metrics collector | Scrapes application and platform metrics |
| Grafana | Metrics visualization | Displays telemetry throughput, database writes, and queue backlog |

---

## 3. Current project capabilities

### Completed

- Docker containerization
- Kubernetes deployments and services
- Persistent storage through PVC
- Redis-based message flow
- Streamlit visualization
- Prometheus monitoring
- Grafana dashboard
- Helm packaging
- GitHub Actions CI/CD
- Argo CD GitOps
- Dev, QA, and Prod namespaces
- Dev to QA to Prod promotion
- Approval gates
- Rollback strategy
- Automated testing and smoke-test control
- Operational documentation

### Planned or design-stage improvements

- Secrets management
- Alertmanager integration
- Horizontal Pod Autoscaling
- Multi-cluster architecture
- Managed-cloud Kubernetes deployment
- Production-oriented database such as PostgreSQL

---

## 4. Suggested repository structure

Your exact folders may differ. Adapt commands to the actual repository paths.

```text
can-cloud-platform/
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── parser/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── parser.py
│   └── decoders/
├── simulator/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── vehicle_data_simulator.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── smoke/
│       └── run_all_smoke_tests.sh
└── .github/
    └── workflows/
        └── ci.yml

can-platform-gitops-helm/
├── applications/
│   ├── dashboard/
│   ├── parser/
│   ├── simulator/
│   ├── redis/
│   └── pvc/
├── environments/
│   ├── dev/
│   ├── qa/
│   └── prod/
└── app-of-apps/
```

---

## 5. End-to-end execution order

Use this dependency-aware order:

```text
1. Start Docker
2. Validate tools
3. Start Minikube
4. Create namespaces
5. Install Argo CD
6. Install Prometheus and Grafana
7. Build application images
8. Run automated tests and smoke tests
9. Load images into Minikube
10. Validate Helm rendering and image tags
11. Apply the Argo CD App-of-Apps
12. Verify PVC and Redis
13. Verify simulator
14. Verify parser
15. Verify dashboard
16. Verify ServiceMonitors and Prometheus targets
17. Open Streamlit, Grafana, Prometheus, and Argo CD
18. Validate the complete telemetry flow
19. Promote Dev to QA and Prod through Git
20. Validate rollback
```

The dependency order matters. Redis must be available before applications that connect to it, and the PVC must be bound before the parser and dashboard rely on the SQLite path.

---

# PART A: HOST AND CLUSTER SETUP

## 6. Start Docker

### Purpose

Docker builds the application images and acts as the Minikube driver in this local setup.

```bash
sudo service docker start
```

### Validate

```bash
docker version
docker ps
```

### Success condition

Both the Docker client and server respond, and `docker ps` completes without a socket or permission error.

---

## 7. Validate required tools

```bash
git --version
python3 --version
docker --version
kubectl version --client
helm version
minikube version
```

### Definition of each tool

- `git`: stores source code and GitOps desired state.
- `python3`: runs the application code and tests.
- `docker`: builds and executes container images.
- `kubectl`: communicates with the Kubernetes API server.
- `helm`: renders and packages Kubernetes resources.
- `minikube`: provides the local Kubernetes cluster.

### Success condition

Every command returns a version.

---

## 8. Start Minikube

```bash
minikube start --driver=docker
```

### Validate

```bash
minikube status
kubectl get nodes -o wide
kubectl cluster-info
```

### Success condition

The Minikube host, kubelet, and API server are running, and the node reports `Ready`.

### Runtime note

Minikube may use containerd inside the node even when Docker is the host driver. If `minikube ssh` followed by `docker images` cannot connect to `/var/run/docker.sock`, use:

```bash
minikube image ls
minikube ssh -- sudo crictl images
```

---

## 9. Create namespaces

```bash
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace qa --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
```

### Purpose

Namespaces isolate platform controllers and application environments.

### Validate

```bash
kubectl get namespaces
```

### Success condition

`argocd`, `monitoring`, `dev`, `qa`, and `prod` are present.

---

# PART B: PLATFORM CONTROLLERS

## 10. Install Argo CD

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Purpose

Argo CD continuously compares the Git-defined desired state with the live Kubernetes state and reconciles differences.

### Validate

```bash
kubectl get pods -n argocd
kubectl rollout status deployment/argocd-server -n argocd
```

### Success condition

Argo CD core pods become Running and Ready.

### Access the UI

```bash
kubectl port-forward -n argocd svc/argocd-server 8080:443
```

Open `https://localhost:8080`.

Retrieve the initial password if still applicable:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
echo
```

---

## 11. Install Prometheus and Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install prometheus \
  prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```

### Purpose

This stack installs Prometheus, Grafana, Prometheus Operator, and monitoring CRDs such as `ServiceMonitor`.

### Validate

```bash
kubectl get pods -n monitoring
kubectl get crd servicemonitors.monitoring.coreos.com
```

### Success condition

Monitoring pods are Running and the ServiceMonitor CRD exists.

---

# PART C: BUILD AND TEST

## 12. Select the build tag

```bash
export BUILD_NUMBER=44
printf 'BUILD_NUMBER=%s\n' "$BUILD_NUMBER"
```

### Purpose

The same immutable tag must be used by Docker, smoke tests, Minikube, Helm values, live Deployments, and GitOps promotion.

---

## 13. Build application images

Run from the source repository root. Adjust build contexts if necessary.

```bash
docker build -t can-dashboard:${BUILD_NUMBER} ./dashboard
docker build -t can-parser:${BUILD_NUMBER} ./parser
docker build -t vehicle-simulator:${BUILD_NUMBER} ./simulator
```

### Validate

```bash
docker images --format '{{.Repository}}:{{.Tag}}' | \
  grep -E "can-dashboard:${BUILD_NUMBER}|can-parser:${BUILD_NUMBER}|vehicle-simulator:${BUILD_NUMBER}"
```

### Success condition

All three images exist with the selected tag.

---

## 14. Automated test stages

### Stage 1: Unit tests

**Definition:** Validate individual Python functions or modules without deploying the complete system.

Example:

```bash
python3 -m pytest tests/unit -v
```

### Stage 2: Static and dependency validation

**Definition:** Validate Python syntax, imports, dependencies, YAML, and Helm rendering.

```bash
python3 -m compileall dashboard parser simulator
helm lint applications/dashboard
helm lint applications/parser
helm lint applications/simulator
```

### Stage 3: Container smoke tests

**Definition:** Validate that each newly built image starts and performs its critical startup behavior.

```bash
chmod +x tests/smoke/*.sh
./tests/smoke/run_all_smoke_tests.sh
```

Check the immediately returned exit code:

```bash
SMOKE_RC=$?
echo "Smoke suite exit code=$SMOKE_RC"
```

- `0`: all smoke tests passed and the pipeline may continue.
- Non-zero: at least one test failed and deployment steps must stop.

### Stage 4: Integration tests

**Definition:** Validate communication between services, such as simulator to Redis and Redis to parser.

Suggested checks:

- Redis responds to `PING`.
- Simulator publishes a message.
- Parser consumes a message.
- Parser writes a decoded row.
- Dashboard can read the database.

### Important rule

A script that prints a Python stack trace must return a non-zero exit code. Cleanup commands such as `docker rm -f` must not hide the application failure.

---

# PART D: LOAD AND PACKAGE IMAGES

## 15. Load images into Minikube

```bash
minikube image load can-dashboard:${BUILD_NUMBER}
minikube image load can-parser:${BUILD_NUMBER}
minikube image load vehicle-simulator:${BUILD_NUMBER}
```

### Purpose

The Helm charts use local images with `imagePullPolicy: Never`. Therefore the exact image tag must already exist inside Minikube.

### Validate

```bash
minikube image ls | \
  grep -E "can-dashboard:${BUILD_NUMBER}|can-parser:${BUILD_NUMBER}|vehicle-simulator:${BUILD_NUMBER}"
```

### Success condition

All three images appear with the selected tag.

### Delete one obsolete image at a time

```bash
minikube ssh
sudo crictl images | grep can-dashboard
sudo crictl rmi <IMAGE_ID>
exit
```

Do not delete an image that is still required by a running or pending workload.

---

## 16. Configure Helm values

Each environment should have an explicit values file. Example:

```yaml
image:
  repository: can-parser
  tag: "44"
  pullPolicy: Never
```

Use separate values for Dev, QA, and Prod:

```text
values-dev.yaml
values-qa.yaml
values-prod.yaml
```

Environment files should differ only where needed, such as image tag, resource limits, replicas, configuration, or feature flags.

### Validate Helm charts

```bash
helm lint applications/dashboard
helm lint applications/parser
helm lint applications/simulator

helm template parser-dev applications/parser \
  -f applications/parser/values-dev.yaml \
  -n dev | grep -n 'image:'
```

### Success condition

Helm renders valid Kubernetes manifests and the expected image tag appears.

---

# PART E: GITOPS DEPLOYMENT

## 17. Understand the two-repository flow

```text
Application source repository
  -> tests
  -> build Docker images
  -> smoke tests
  -> update GitOps image tag

GitOps repository
  -> Helm charts and environment values
  -> Argo CD detects commit
  -> Argo CD syncs Kubernetes
```

GitHub Actions is responsible for CI and controlled configuration updates. Argo CD is responsible for reconciling the committed desired state into Kubernetes.

---

## 18. Apply the App-of-Apps root

Use the actual path from the GitOps repository:

```bash
kubectl apply -f <path-to-app-of-apps.yaml>
```

### Purpose

The root application creates and manages the child applications for Dev, QA, and Prod.

### Validate

```bash
kubectl get applications -n argocd
kubectl get applicationsets -n argocd
```

### Success condition

Expected child applications appear and eventually report `Synced` and `Healthy`.

---

## 19. Validate every namespace

Always use namespace-qualified commands. A plain `kubectl get pods` checks only the active namespace, often `default`.

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get services -A
kubectl get pvc -A
```

Focused checks:

```bash
kubectl get pods,svc,pvc -n dev
kubectl get pods,svc,pvc -n qa
kubectl get pods,svc,pvc -n prod
```

### Success condition

Redis, simulator, parser, and dashboard are Running and Ready in each intended environment, and each PVC is Bound.

---

## 20. Validate image-tag consistency

```bash
minikube image ls | grep -E 'can-dashboard|can-parser|vehicle-simulator'

kubectl get deployment -A \
  -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,IMAGE:.spec.template.spec.containers[0].image'

helm template parser-dev applications/parser \
  -f applications/parser/values-dev.yaml \
  -n dev | grep -n 'image:'
```

### Success condition

These three references match exactly:

1. Image loaded into Minikube
2. Image rendered by Helm
3. Image used by the live Deployment

### `ErrImageNeverPull`

This status means the pod references an image that is absent from the node while `imagePullPolicy` is `Never`.

Diagnose:

```bash
kubectl get pod <pod-name> -n <namespace> \
  -o jsonpath='{.spec.containers[0].image}'
echo

minikube image ls | grep can-parser
```

Fix either the GitOps/Helm tag or load the exact required image.

---

# PART F: APPLICATION VALIDATION

## 21. Validate PVC storage

```bash
kubectl get pvc -A
```

### Success condition

The required claims are `Bound` in Dev, QA, and Prod.

### Warning

Deleting a PVC can delete persisted SQLite data. Back up required data before resetting a claim.

---

## 22. Validate Redis

Find the service name first:

```bash
kubectl get svc -n dev | grep redis
```

Validate from a temporary pod:

```bash
kubectl run redis-check \
  --rm -it \
  --restart=Never \
  -n dev \
  --image=redis:7-alpine \
  -- redis-cli -h redis ping
```

Expected:

```text
PONG
```

If the actual service has another name, replace `redis` with that service name.

---

## 23. Validate simulator

```bash
kubectl get pods -n dev | grep simulator
kubectl logs -n dev deployment/vehicle-simulator-dev --tail=100
```

If the deployment name differs:

```bash
kubectl get deployments -n dev
```

### Success condition

- Pod is Running and Ready.
- Logs show CAN frame generation or publishing.
- No Redis DNS or connection exception appears.

---

## 24. Validate parser

```bash
kubectl get pods -n dev | grep parser
kubectl logs -n dev deployment/parser-dev --tail=100
kubectl describe pod -n dev <parser-pod-name>
```

For a previous crash:

```bash
kubectl logs -n dev deployment/parser-dev --previous --tail=100
```

### Success condition

- Parser pod is Running and Ready.
- Redis connection succeeds.
- CAN frames are decoded.
- SQLite writes succeed.
- No `OperationalError`, `ConnectionError`, or traceback appears.

---

## 25. Validate SQLite data

First inspect the parser deployment for the mounted path:

```bash
kubectl get deployment parser-dev -n dev -o yaml | \
  grep -A8 -E 'volumeMounts:|mountPath:|volumes:'
```

Then execute the appropriate database query. Replace the path with the path used by the deployment:

```bash
kubectl exec -n dev deployment/parser-dev -- \
  python -c "import sqlite3; c=sqlite3.connect('/data/decoded.db'); print(c.execute('select count(*) from decoded_data').fetchone())"
```

Replace `decoded_data` with the actual table name.

### Success condition

The database opens and returns a row count without a permission or missing-directory error.

---

## 26. Validate dashboard

```bash
kubectl get svc -n dev | grep dashboard
minikube service <dashboard-service-name> -n dev --url
```

Validate HTTP response:

```bash
DASHBOARD_URL=$(minikube service <dashboard-service-name> -n dev --url)
curl -I "$DASHBOARD_URL"
```

### Success condition

The service URL is reachable and the Streamlit page loads with decoded vehicle data.

---

# PART G: OBSERVABILITY

## 27. Metrics and their meaning

| Metric | Type | Meaning |
|---|---|---|
| `can_frames_generated_total` | Counter | Total CAN frames generated by the simulator |
| `decoded_messages_total` | Counter | Total messages decoded by the parser |
| `sqlite_writes_total` | Counter | Total decoded records written to SQLite |
| `redis_queue_depth` | Gauge | Current Redis backlog |

Counters continuously increase until a process restarts. Use `rate()` to calculate throughput. A gauge represents a current state and can be graphed directly.

Suggested queries:

```promql
rate(can_frames_generated_total[1m])
rate(decoded_messages_total[1m])
rate(sqlite_writes_total[1m])
redis_queue_depth
```

---

## 28. Validate ServiceMonitors

```bash
kubectl get servicemonitor -A
```

### Success condition

Expected parser and simulator ServiceMonitors exist for the intended environments.

If resources exist but Prometheus targets are absent, compare ServiceMonitor selectors with Service labels:

```bash
kubectl get servicemonitor <name> -n <namespace> -o yaml
kubectl get service <name> -n <namespace> --show-labels
```

---

## 29. Access Prometheus

```bash
kubectl port-forward -n monitoring \
  svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Open `http://localhost:9090` and check targets and PromQL results.

### Success condition

Parser and simulator targets are UP, and all required metrics return samples.

---

## 30. Access Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Retrieve the administrator password:

```bash
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath='{.data.admin-password}' | base64 -d
echo
```

Open `http://localhost:3000`.

### Recommended panels

1. CAN frames generated per second
2. Messages decoded per second
3. SQLite writes per second
4. Redis queue depth
5. Parser CPU and memory, if configured
6. Simulator CPU and memory, if configured

### Interpretation

If generation rate stays higher than decoding rate and queue depth rises continuously, the parser is not keeping up with the producer.

---

# PART H: CI/CD, PROMOTION, APPROVAL, AND ROLLBACK

## 31. GitHub Actions pipeline flow

```text
Checkout source
  -> generate build tag
  -> unit/static checks
  -> build three images
  -> container smoke tests
  -> integration tests
  -> load/publish artifacts
  -> update Dev Helm value
  -> commit GitOps change
  -> Argo CD deploys Dev
  -> validate Dev
  -> approval gate
  -> promote same tag to QA
  -> validate QA
  -> approval gate
  -> promote same tag to Prod
  -> validate Prod
```

### Mandatory quality-gate behavior

```bash
./tests/smoke/run_all_smoke_tests.sh
```

- Exit `0`: next step executes.
- Non-zero: workflow fails and later dependent steps are skipped.

Do not use `continue-on-error: true` for mandatory tests.

---

## 32. Dev to QA to Prod promotion

Promotion should reuse the same validated image tag rather than rebuilding different binaries for each environment.

Example Dev values update:

```bash
yq -i '.image.tag = "44"' applications/parser/values-dev.yaml
git add applications/parser/values-dev.yaml
git commit -m "Promote parser image 44 to dev"
git push
```

Example QA promotion after Dev validation:

```bash
yq -i '.image.tag = "44"' applications/parser/values-qa.yaml
git add applications/parser/values-qa.yaml
git commit -m "Promote parser image 44 to qa"
git push
```

Apply the same pattern to dashboard and simulator, and then to Prod after approval.

### Validate after each promotion

```bash
kubectl get applications -n argocd
kubectl rollout status deployment/<deployment-name> -n <environment>
kubectl get pods -n <environment>
```

---

## 33. Approval gates

### Definition

An approval gate prevents a higher-environment deployment until the named approver accepts the promotion.

### Recommended placement

- After Dev validation and before QA promotion
- After QA validation and before Prod promotion

### Approval evidence

- The tested image tag
- Test results
- Argo CD health
- Deployment status
- Rollback target
- Summary of change

---

## 34. Rollback strategy

### GitOps rollback, recommended

Restore the previous known-good image tag in Git and push the commit.

```bash
git log --oneline -- applications/parser/values-prod.yaml
git revert <commit-sha>
git push
```

Argo CD then reconciles the previous desired state.

### Kubernetes rollout undo, emergency-only

```bash
kubectl rollout history deployment/<deployment-name> -n <namespace>
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

Because Argo CD controls desired state, also update or revert Git. Otherwise Argo CD may restore the undesired Git-defined version.

### Validate rollback

```bash
kubectl rollout status deployment/<deployment-name> -n <namespace>
kubectl get pods -n <namespace>
kubectl get deployment <deployment-name> -n <namespace> \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
echo
```

Then repeat health, log, smoke, and dashboard validation.

---

# PART I: OPERATIONS AND TROUBLESHOOTING

## 35. Common diagnostic commands

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get services -A
kubectl get pvc -A
kubectl get applications -n argocd
kubectl get servicemonitor -A
kubectl get events -A --sort-by=.lastTimestamp
minikube image ls
```

---

## 36. Pod troubleshooting flow

```bash
kubectl get pods -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --tail=200
kubectl logs <pod-name> -n <namespace> --previous --tail=200
```

Interpret the status first:

| Status | Typical meaning |
|---|---|
| `ErrImageNeverPull` | Required local image/tag is absent and pull policy is Never |
| `ImagePullBackOff` | Registry pull failed |
| `CrashLoopBackOff` | Container starts and repeatedly crashes |
| `Pending` | Scheduling, PVC, resource, or node constraint |
| `Running` but `0/1` Ready | Readiness probe or application initialization failure |

---

## 37. Helm troubleshooting

See releases:

```bash
helm list -A
```

Render without applying:

```bash
helm template <release> <chart-path> -f <values-file> -n <namespace>
```

Upgrade directly only when that release is intentionally managed with Helm CLI:

```bash
helm upgrade --install <release> <chart-path> \
  -f <values-file> \
  -n <namespace> \
  --create-namespace
```

For Argo CD-managed resources, prefer committing values changes to Git rather than making unexplained manual cluster changes.

---

## 38. Redis connection errors

Error example:

```text
Error connecting to redis:6379. Name or service not known
```

Validate:

```bash
kubectl get svc -n <namespace> | grep redis
kubectl get endpoints -n <namespace> | grep redis
kubectl exec -n <namespace> deployment/<application> -- getent hosts redis
```

Check that:

- Service name matches the configured hostname.
- Service and consumer are in the expected namespace.
- Redis pod is Ready.
- Service has endpoints.
- Port `6379` is correct.

---

## 39. SQLite database errors

Error example:

```text
sqlite3.OperationalError: unable to open database file
```

Validate:

```bash
kubectl exec -n <namespace> deployment/<parser-deployment> -- \
  sh -c 'id; env | grep -E "DB|SQLITE"; mount; ls -ld <database-directory>'
```

Check that:

- Parent directory exists.
- Container user has write permission.
- PVC is Bound.
- Volume is mounted at the configured path.
- Parser and dashboard agree on the database location.

---

## 40. Port-forward conflicts

```bash
lsof -i :8080
lsof -i :9090
lsof -i :3000
lsof -i :8501
```

Stop an obsolete process only after identifying it:

```bash
kill <PID>
```

Run each active port-forward in a separate terminal.

---

## 41. Safe restart commands

Restart a deployment:

```bash
kubectl rollout restart deployment/<deployment-name> -n <namespace>
kubectl rollout status deployment/<deployment-name> -n <namespace>
```

Delete one pod and allow the Deployment to recreate it:

```bash
kubectl delete pod <pod-name> -n <namespace>
```

A Helm values update that does not change the rendered pod template will not restart pods. A tag, environment variable, annotation, ConfigMap checksum, or other pod-template change creates a new ReplicaSet.

---

# PART J: COMPLETE ACCEPTANCE TEST

## 42. Final platform validation

### Cluster and GitOps

```bash
minikube status
kubectl get nodes
kubectl get applications -n argocd
```

Expected: node Ready; Argo CD applications Synced and Healthy.

### Application environments

```bash
kubectl get pods -n dev
kubectl get pods -n qa
kubectl get pods -n prod
kubectl get pvc -A
```

Expected: workloads Ready and PVCs Bound.

### Data flow

1. Confirm simulator logs show generated frames.
2. Confirm Redis is reachable and has expected queue activity.
3. Confirm parser logs show decoding and writes.
4. Query SQLite for decoded rows.
5. Open Streamlit and confirm values and trends.

### Observability

```bash
kubectl get servicemonitor -A
kubectl get pods -n monitoring
```

Expected: parser and simulator targets UP in Prometheus and panels populated in Grafana.

### Delivery control

1. Confirm smoke tests fail the workflow when a critical image test fails.
2. Confirm a successful build updates only the intended environment value.
3. Confirm approval is required before higher-environment promotion.
4. Confirm rollback restores the previous image tag and healthy state.

---

## 43. Definition of done

The project is ready for demonstration when:

- Docker images build successfully.
- Automated tests return accurate exit codes.
- Exact image tags are loaded in Minikube.
- Helm renders the intended tag and configuration.
- Argo CD applications are Synced and Healthy.
- Redis, simulator, parser, and dashboard are Ready.
- PVCs are Bound and SQLite writes succeed.
- CAN data flows from simulator to Redis to parser to SQLite to dashboard.
- Prometheus targets are UP.
- Grafana displays platform metrics.
- Dev to QA to Prod promotion is traceable through Git.
- Approval gates prevent uncontrolled promotion.
- Rollback to a known-good version has been validated.

---

## 44. Manager/demo sequence

1. Open Streamlit and show changing vehicle signals.
2. Explain the flow: simulator to Redis to parser to SQLite to dashboard.
3. Show `kubectl get pods -A` and PVC status.
4. Open Grafana and explain generation, decoding, writes, and queue depth.
5. Show GitHub Actions quality gates and build tag.
6. Show the GitOps values and Argo CD sync status.
7. Explain Dev to QA to Prod promotion and approvals.
8. Demonstrate or describe rollback to the previous known-good tag.
9. Close with planned production improvements: secrets, alerts, autoscaling, multi-cluster, managed Kubernetes, and production database.

---

## 45. Cleanup and reset

### Stop local access processes

Stop active `kubectl port-forward` commands with `Ctrl+C` in their terminals.

### Delete only application namespaces

```bash
kubectl delete namespace dev qa prod
```

### Delete the complete Minikube cluster

```bash
minikube delete --all --purge
```

This removes the local cluster, workloads, and node-local images. Back up important SQLite/PVC data first.

---

## 46. Primary operational rule

For every platform change, follow this control loop:

```text
Change -> Test -> Build -> Tag -> Update Git -> Sync -> Verify -> Promote or Roll Back
```

Never promote only because an image was built. Promote only after tests, runtime health, data-flow validation, and environment approval provide evidence that the same immutable version is ready for the next stage.
