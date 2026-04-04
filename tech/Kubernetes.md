# Kubernetes

## What is Kubernetes
```
overview:
  full_name: Kubernetes (K8s)
  type: Container orchestration platform
  use_as:
    - Container management
    - Service deployment & scaling
    - Load balancing
    - Self-healing infrastructure
    - Rolling deployments
  written_in: Go
  license: Apache 2.0
  created_by: Google (now CNCF)
  default_api_port: 6443

key_features:
  - Automatic container scheduling and placement
  - Self-healing (restarts failed containers, replaces unhealthy nodes)
  - Horizontal auto-scaling (scale pods based on CPU/memory/custom metrics)
  - Service discovery and load balancing
  - Rolling updates with zero downtime
  - Secret and configuration management
  - Storage orchestration
  - Declarative configuration (desired state, not imperative steps)
```

## Core Architecture
```
architecture:
  control_plane:
    description: The brain of the cluster, makes global decisions
    components:
      api_server:
        description: Frontend for the Kubernetes API
        role: All communication goes through it (kubectl, other components)
        port: 6443

      etcd:
        description: Distributed key-value store
        role: Stores all cluster state and configuration
        note: Only component that stores state, backup this!

      scheduler:
        description: Assigns pods to nodes
        role: Watches for unscheduled pods, picks best node based on resources

      controller_manager:
        description: Runs controller loops
        controllers:
          - Node controller (detects node failures)
          - ReplicaSet controller (maintains correct pod count)
          - Endpoint controller (populates services)
          - Service account controller

  worker_nodes:
    description: Machines that run your containers
    components:
      kubelet:
        description: Agent on each node
        role: Ensures containers in pods are running and healthy

      kube_proxy:
        description: Network proxy on each node
        role: Maintains network rules, enables Service abstraction

      container_runtime:
        description: Software that runs containers
        options: containerd, CRI-O (Docker deprecated as runtime)
```

## Core Concepts
```
objects:
  pod:
    description: Smallest deployable unit, one or more containers
    properties:
      - Shared network namespace (localhost between containers)
      - Shared storage volumes
      - Ephemeral (can be killed and recreated anytime)
      - Gets a unique IP within the cluster
    note: Never create bare pods, always use a controller (Deployment, etc.)

  deployment:
    description: Manages ReplicaSets and provides declarative updates
    features:
      - Rolling updates and rollbacks
      - Scaling up/down
      - Manages pod lifecycle
    use_for: Stateless applications (web servers, APIs)

  service:
    description: Stable network endpoint for a set of pods
    why: Pods are ephemeral with changing IPs; Services provide stable DNS/IP
    types:
      ClusterIP: Internal-only (default), accessible within cluster
      NodePort: Exposes on each node's IP at a static port (30000-32767)
      LoadBalancer: Provisions cloud load balancer (AWS ELB, GCP LB)
      ExternalName: Maps to external DNS name

  namespace:
    description: Virtual cluster within a cluster
    use_for: Isolating environments (dev, staging, prod) or teams
    defaults: default, kube-system, kube-public, kube-node-lease

  configmap:
    description: Store non-secret configuration as key-value pairs
    inject_as: Environment variables or mounted files

  secret:
    description: Store sensitive data (passwords, tokens, keys)
    encoding: Base64 encoded (NOT encrypted by default)
    inject_as: Environment variables or mounted files

  ingress:
    description: HTTP/HTTPS routing rules for external traffic
    features: Host-based routing, path-based routing, TLS termination
    requires: Ingress controller (nginx, traefik, etc.)

  persistent_volume:
    pv: Storage resource provisioned by admin
    pvc: Request for storage by a pod
    flow: Admin creates PV -> User creates PVC -> Pod mounts PVC

  statefulset:
    description: Like Deployment but for stateful applications
    guarantees: Stable network identity, ordered deployment, persistent storage
    use_for: Databases, Kafka, ZooKeeper

  daemonset:
    description: Ensures a pod runs on every (or selected) node
    use_for: Log collectors, monitoring agents, network plugins

  job:
    description: Runs a pod to completion (then stops)
    use_for: Batch processing, data migration, one-time tasks

  cronjob:
    description: Runs Jobs on a schedule (cron syntax)
    use_for: Scheduled backups, report generation, cleanup tasks
```

## When to Use Kubernetes
```
use_cases:
  microservices:
    description: Deploy and manage dozens of services
    why: Service discovery, load balancing, independent scaling
    example: 20 microservices each in their own Deployment + Service

  auto_scaling:
    description: Scale based on traffic or resource usage
    why: HPA scales pods, Cluster Autoscaler scales nodes
    example: Scale API from 3 to 50 pods during traffic spike

  zero_downtime_deployments:
    description: Update applications without any downtime
    why: Rolling updates replace pods gradually
    example: Deploy v2 of your app while v1 still serves traffic

  multi_environment:
    description: Run dev, staging, prod on same cluster
    why: Namespaces provide isolation, resource quotas prevent overuse
    example: namespace/dev, namespace/staging, namespace/prod

  hybrid_cloud:
    description: Run across multiple cloud providers or on-prem
    why: K8s abstracts infrastructure, same manifests everywhere
    example: Same app on AWS EKS and on-prem bare metal
```

## When NOT to Use Kubernetes
```
avoid_when:
  - Small team with 1-3 services (use Docker Compose or a PaaS)
  - Simple static sites or single-container apps
  - Team lacks operational expertise (steep learning curve)
  - Budget is tight (control plane + monitoring overhead)
  - Serverless fits better (AWS Lambda for event-driven workloads)
```

## Installation & Local Setup
```
local_options:
  minikube:
    description: Single-node K8s cluster in a VM
    install: |
      curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
      sudo install minikube-linux-amd64 /usr/local/bin/minikube
    start: minikube start
    dashboard: minikube dashboard

  kind:
    description: K8s in Docker (runs nodes as containers)
    install: go install sigs.k8s.io/kind@latest
    start: kind create cluster

  k3s:
    description: Lightweight K8s distribution
    install: curl -sfL https://get.k3s.io | sh -
    note: Great for edge, IoT, CI/CD

  kubectl:
    description: CLI tool for interacting with K8s
    install: |
      curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
      sudo install kubectl /usr/local/bin/kubectl
    verify: kubectl version --client
```

## Essential kubectl Commands
```
kubectl_commands:
  cluster_info:
    get_info: kubectl cluster-info
    get_nodes: kubectl get nodes
    get_all: kubectl get all
    get_namespaces: kubectl get namespaces

  pods:
    list: kubectl get pods
    list_all_ns: kubectl get pods --all-namespaces
    describe: kubectl describe pod <pod-name>
    logs: kubectl logs <pod-name>
    logs_follow: kubectl logs -f <pod-name>
    logs_container: kubectl logs <pod-name> -c <container-name>
    exec_shell: kubectl exec -it <pod-name> -- /bin/sh
    delete: kubectl delete pod <pod-name>
    port_forward: kubectl port-forward <pod-name> 8080:80

  deployments:
    list: kubectl get deployments
    create: kubectl create deployment nginx --image=nginx
    scale: kubectl scale deployment nginx --replicas=5
    update_image: kubectl set image deployment/nginx nginx=nginx:1.25
    rollout_status: kubectl rollout status deployment/nginx
    rollback: kubectl rollout undo deployment/nginx
    history: kubectl rollout history deployment/nginx

  services:
    list: kubectl get services
    expose: kubectl expose deployment nginx --port=80 --type=LoadBalancer
    describe: kubectl describe service <svc-name>

  apply_manifests:
    apply: kubectl apply -f manifest.yaml
    apply_dir: kubectl apply -f ./k8s/
    delete: kubectl delete -f manifest.yaml
    dry_run: kubectl apply -f manifest.yaml --dry-run=client

  debugging:
    events: kubectl get events --sort-by='.lastTimestamp'
    top_pods: kubectl top pods
    top_nodes: kubectl top nodes
    describe_node: kubectl describe node <node-name>

  context:
    list: kubectl config get-contexts
    switch: kubectl config use-context <context-name>
    current: kubectl config current-context
```

## YAML Manifests

### Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  containers:
    - name: my-app
      image: my-app:1.0
      ports:
        - containerPort: 8080
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 5
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 3
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # max extra pods during update
      maxUnavailable: 0     # zero downtime
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:1.0
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: log-level
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  type: ClusterIP       # or NodePort, LoadBalancer
  ports:
    - protocol: TCP
      port: 80          # service port
      targetPort: 8080  # container port
```

### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
  tls:
    - hosts:
        - myapp.example.com
      secretName: tls-secret
```

### ConfigMap and Secret
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  log-level: "info"
  max-connections: "100"
  config.yaml: |
    server:
      port: 8080
      timeout: 30s
---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: cG9zdGdyZXM6Ly91c2VyOnBhc3NAaG9zdDo1NDMyL2Ri    # base64 encoded
  api-key: c2VjcmV0LWtleS0xMjM=                                  # base64 encoded
```

### HorizontalPodAutoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### PersistentVolumeClaim
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

### CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"    # every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:15
              command: ["pg_dump", "-h", "db-host", "-U", "admin", "-d", "mydb"]
          restartPolicy: OnFailure
```

## Small Application: Deploy a Go API on Kubernetes
```
app_overview:
  name: Go REST API on K8s
  description: |
    Full deployment of a Go API with:
    1. Deployment with 3 replicas
    2. Service for internal load balancing
    3. Ingress for external access
    4. ConfigMap for settings
    5. HPA for auto-scaling
```

### The Go Application
```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "os"
    "time"
)

type Response struct {
    Message   string `json:"message"`
    Hostname  string `json:"hostname"`
    Version   string `json:"version"`
    Timestamp string `json:"timestamp"`
}

func main() {
    version := os.Getenv("APP_VERSION")
    if version == "" {
        version = "1.0.0"
    }

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        hostname, _ := os.Hostname()
        resp := Response{
            Message:   "Hello from Kubernetes!",
            Hostname:  hostname,
            Version:   version,
            Timestamp: time.Now().Format(time.RFC3339),
        }
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(resp)
    })

    http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ok"))
    })

    http.HandleFunc("/ready", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ready"))
    })

    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### Dockerfile
```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod main.go ./
RUN go build -o server .

FROM alpine:3.19
COPY --from=builder /app/server /server
EXPOSE 8080
CMD ["/server"]
```

### Complete K8s Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: my-app
data:
  APP_VERSION: "1.0.0"
---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: my-app:1.0
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: app-config
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "200m"
              memory: "128Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 3
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: my-app
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8080
---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Deploy Commands
```
deploy_steps:
  build: docker build -t my-app:1.0 .
  apply_all: kubectl apply -f k8s/
  check_pods: kubectl get pods -n my-app
  check_service: kubectl get svc -n my-app
  check_hpa: kubectl get hpa -n my-app
  port_forward: kubectl port-forward svc/api-service 8080:80 -n my-app
  test: curl http://localhost:8080
  scale_manual: kubectl scale deployment api --replicas=5 -n my-app
  update: kubectl set image deployment/api api=my-app:2.0 -n my-app
  rollback: kubectl rollout undo deployment/api -n my-app
  logs: kubectl logs -f deployment/api -n my-app
  cleanup: kubectl delete namespace my-app
```

## Common Patterns
```
patterns:
  sidecar:
    description: Helper container alongside main container in same pod
    use_case: Log shipping, proxy, config reloading
    example: Envoy proxy sidecar for service mesh

  init_container:
    description: Container that runs before main container starts
    use_case: DB migration, config download, wait for dependency
    example: Wait for database to be ready before app starts

  ambassador:
    description: Proxy container that handles external communication
    use_case: API gateway, connection pooling

  blue_green:
    description: Run two identical environments, switch traffic
    flow: Deploy v2 alongside v1 -> test v2 -> switch Service selector -> delete v1

  canary:
    description: Route small percentage of traffic to new version
    flow: Deploy v2 with 1 replica -> monitor -> gradually increase -> full rollout

  horizontal_pod_autoscaling:
    description: Auto-scale pods based on metrics
    flow: Load increases -> HPA adds pods -> load decreases -> HPA removes pods
```

## Tags
```
tags:
  - kubernetes
  - k8s
  - container-orchestration
  - devops
  - cloud-native
  - microservices
  - deployment
```
