# CI CD

## What is CI/CD
```
overview:
  definition: |
    CI/CD is a set of practices that automate the process of
    integrating code changes, testing them, and deploying to
    production. It enables teams to deliver software faster
    and more reliably.

  components:
    continuous_integration:
      description: |
        Developers merge code to main branch frequently (multiple times/day).
        Each merge triggers automated build and tests.
      goal: Catch bugs early, avoid integration hell
      key_practices:
        - Commit to main/trunk frequently (at least daily)
        - Every commit triggers automated build + tests
        - Fix broken builds immediately (top priority)
        - Keep the build fast (< 10 minutes ideal)

    continuous_delivery:
      description: |
        Code is always in a deployable state. Deployment to production
        requires manual approval (push-button release).
      goal: Release at any time with confidence
      key_practices:
        - Automated testing at every stage
        - Staging environment mirrors production
        - One-click deployment to production
        - Human decides WHEN to deploy

    continuous_deployment:
      description: |
        Every change that passes all tests is automatically deployed
        to production. No manual approval step.
      goal: Ship every change to users as fast as possible
      key_practices:
        - Full test automation (no manual QA gate)
        - Feature flags for incomplete features
        - Robust monitoring and rollback
        - High confidence in test suite

  progression: |
    CI -> Continuous Delivery -> Continuous Deployment
    (each builds on the previous)
    Most teams do CI + Continuous Delivery.
    Continuous Deployment requires very mature testing/monitoring.
```

## Pipeline Stages
```
pipeline:
  description: |
    A pipeline is a series of automated steps that code goes through
    from commit to production.

  stages:
    1_source:
      trigger: "Code pushed to repository (git push)"
      actions:
        - "Webhook notifies CI server"
        - "CI server clones repository"
        - "Determines which pipeline to run"

    2_build:
      description: Compile code and create artifacts
      actions:
        - "Install dependencies (go mod download, npm install)"
        - "Compile source code (go build, tsc)"
        - "Build Docker image"
        - "Generate code (protobuf, swagger)"
      artifacts:
        - Binary executable
        - Docker image
        - Static assets bundle

    3_test:
      description: Run automated tests at multiple levels
      levels:
        unit_tests: "Test individual functions (fastest, run first)"
        integration_tests: "Test service with real DB/Redis (slower)"
        e2e_tests: "Test full user flows (slowest, run last)"
      also:
        - "Linting and static analysis"
        - "Security scanning (SAST, dependency audit)"
        - "Code coverage reporting"

    4_staging:
      description: Deploy to staging environment for final validation
      actions:
        - "Deploy to staging (mirrors production)"
        - "Run smoke tests against staging"
        - "Performance testing"
        - "Manual QA (if continuous delivery, not deployment)"

    5_deploy:
      description: Release to production
      actions:
        - "Deploy using chosen strategy (blue-green, canary, rolling)"
        - "Run smoke tests against production"
        - "Monitor error rates and latency"
        - "Rollback if issues detected"
```

## Deployment Strategies
```
deployment_strategies:

  rolling:
    description: Gradually replace old instances with new ones
    how: |
      1. Start new instance with new version
      2. Wait until healthy
      3. Remove one old instance
      4. Repeat until all instances are new
    pros:
      - No additional infrastructure needed
      - Gradual rollout
      - Zero downtime
    cons:
      - Both versions run simultaneously during rollout
      - Rollback requires another rolling update
      - Can be slow with many instances
    best_for: Most standard deployments

  blue_green:
    description: Two identical environments, swap traffic between them
    how: |
      1. Blue (current) serves all traffic
      2. Deploy new version to Green
      3. Test Green thoroughly
      4. Switch load balancer from Blue to Green
      5. Blue becomes standby (instant rollback)
    pros:
      - Instant rollback (switch back to Blue)
      - Full testing before any user sees new version
      - Zero downtime
    cons:
      - Requires double the infrastructure
      - Database migrations must be backwards-compatible
    best_for: Risk-averse deployments, critical services

  canary:
    description: Route small percentage of traffic to new version
    how: |
      1. Deploy new version alongside old
      2. Route 5% of traffic to new version
      3. Monitor error rates, latency, user feedback
      4. If good, gradually increase (10%, 25%, 50%, 100%)
      5. If bad, route all traffic back to old version
    pros:
      - Minimal blast radius (only % of users affected)
      - Real production traffic validation
      - Quick rollback
    cons:
      - More complex routing setup
      - Need good monitoring to detect issues
      - Database must support both versions
    best_for: High-traffic services, validating with real users

  recreate:
    description: Stop all old instances, start all new instances
    how: |
      1. Shut down all old instances
      2. Deploy new version
      3. Start all new instances
    pros:
      - Simple
      - No version compatibility issues
    cons:
      - Downtime during deployment
    best_for: Development/staging environments, non-critical services

  feature_flags:
    description: Deploy code but control activation via configuration
    how: |
      1. Deploy new feature behind a flag (disabled)
      2. Enable flag for internal users (testing)
      3. Enable for 10% of users (canary)
      4. Enable for 100% (full rollout)
      5. Remove flag and old code path
    tools:
      - LaunchDarkly
      - Unleash (open source)
      - Flagsmith
      - Custom (Redis/DB toggle)
    pros:
      - Decouple deployment from release
      - Instant enable/disable without deploy
      - A/B testing
```

## Example - GitHub Actions Pipeline
```
github_actions:
  file: .github/workflows/ci-cd.yml
```

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Run linter
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest

  test:
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Run unit tests
        run: go test -v -race -coverprofile=coverage.out ./...

      - name: Run integration tests
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/testdb?sslmode=disable
          REDIS_URL: localhost:6379
        run: go test -v -tags=integration ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.out

  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging

    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --namespace=staging
          kubectl rollout status deployment/myapp --namespace=staging --timeout=300s

      - name: Run smoke tests
        run: |
          curl -f https://staging.example.com/health || exit 1

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production

    steps:
      - name: Deploy to production (canary)
        run: |
          kubectl set image deployment/myapp-canary \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --namespace=production

      - name: Monitor canary (5 min)
        run: |
          sleep 300
          ERROR_RATE=$(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_errors_total[5m])' | jq '.data.result[0].value[1]')
          if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
            echo "Error rate too high, rolling back"
            kubectl rollout undo deployment/myapp-canary --namespace=production
            exit 1
          fi

      - name: Full rollout
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --namespace=production
          kubectl rollout status deployment/myapp --namespace=production --timeout=600s
```

## Example - Dockerfile for Go Service
```
dockerfile:
  file: Dockerfile
```

```go
// main.go - example service
package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
)

func main() {
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("OK"))
    })

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        version := os.Getenv("APP_VERSION")
        fmt.Fprintf(w, "Hello from version %s", version)
    })

    log.Printf("Server starting on :%s", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}
```

```
dockerfile_content: |
  # Build stage
  FROM golang:1.22-alpine AS builder
  WORKDIR /app

  # Cache dependencies
  COPY go.mod go.sum ./
  RUN go mod download

  # Build binary
  COPY . .
  RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server .

  # Runtime stage
  FROM alpine:3.19
  RUN apk --no-cache add ca-certificates tzdata
  RUN adduser -D -g '' appuser

  COPY --from=builder /app/server /usr/local/bin/server

  USER appuser
  EXPOSE 8080

  HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

  ENTRYPOINT ["server"]
```

## Example - Makefile for CI Tasks
```
makefile:
  file: Makefile
  content: |
    APP_NAME := myapp
    VERSION := $(shell git describe --tags --always --dirty)
    REGISTRY := ghcr.io/myorg

    .PHONY: all build test lint docker-build docker-push deploy

    all: lint test build

    build:
    	go build -ldflags="-X main.version=$(VERSION)" -o bin/$(APP_NAME) .

    test:
    	go test -v -race -coverprofile=coverage.out ./...

    test-integration:
    	go test -v -tags=integration ./...

    lint:
    	golangci-lint run ./...

    docker-build:
    	docker build -t $(REGISTRY)/$(APP_NAME):$(VERSION) .
    	docker tag $(REGISTRY)/$(APP_NAME):$(VERSION) $(REGISTRY)/$(APP_NAME):latest

    docker-push:
    	docker push $(REGISTRY)/$(APP_NAME):$(VERSION)
    	docker push $(REGISTRY)/$(APP_NAME):latest

    deploy-staging:
    	kubectl set image deployment/$(APP_NAME) $(APP_NAME)=$(REGISTRY)/$(APP_NAME):$(VERSION) -n staging

    deploy-prod:
    	kubectl set image deployment/$(APP_NAME) $(APP_NAME)=$(REGISTRY)/$(APP_NAME):$(VERSION) -n production

    clean:
    	rm -rf bin/ coverage.out
```

## Best Practices
```
best_practices:
  ci:
    - "Run tests on every push and pull request"
    - "Keep builds fast (< 10 min) - parallelize, cache dependencies"
    - "Fail fast: run linters and unit tests before heavier tests"
    - "Use matrix builds for multiple OS/language versions"
    - "Pin dependency versions (go.sum, package-lock.json)"
    - "Never store secrets in code - use CI secrets/vault"

  cd:
    - "Deploy the same artifact to all environments (don't rebuild)"
    - "Use environment variables for config (not different builds)"
    - "Automate database migrations as part of the pipeline"
    - "Always have a rollback plan (blue-green or versioned artifacts)"
    - "Use feature flags to decouple deploy from release"

  testing:
    - "Unit tests: fast, isolated, no external dependencies"
    - "Integration tests: use Docker containers for dependencies"
    - "E2E tests: run against staging, not production"
    - "Require minimum code coverage (e.g., 80%) but don't chase 100%"
    - "Run security scanning (Snyk, Trivy) in pipeline"

  docker:
    - "Use multi-stage builds (small final image)"
    - "Run as non-root user"
    - "Add HEALTHCHECK instruction"
    - "Pin base image versions (don't use :latest in prod)"
    - "Cache dependency layers (COPY go.mod before COPY .)"
    - "Scan images for vulnerabilities (Trivy, Snyk Container)"

  git:
    - "Use short-lived feature branches (merge within 1-2 days)"
    - "Require PR reviews before merge to main"
    - "Use conventional commits (feat:, fix:, chore:)"
    - "Tag releases with semantic versioning"
    - "Protect main branch (no direct pushes)"
```

## Tags
```
tags:
  - ci-cd
  - devops
  - github-actions
  - docker
  - deployment
  - automation
```
