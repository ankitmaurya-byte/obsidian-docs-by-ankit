# Monitoring & Logging

## What is Observability
```
overview:
  definition: |
    Observability is the ability to understand the internal state
    of a system by examining its external outputs. It answers:
    "Why is the system behaving this way?"

  three_pillars:
    logs:
      description: Discrete timestamped records of events
      answers: "What happened?"
      example: "2026-03-30T10:15:30Z ERROR failed to process order order_id=123 err=timeout"

    metrics:
      description: Numeric measurements aggregated over time
      answers: "How is the system performing?"
      example: "http_request_duration_seconds{method=GET, path=/api/users} = 0.045"

    traces:
      description: End-to-end path of a request through distributed services
      answers: "Where is the bottleneck?"
      example: "Request 'abc' -> API Gateway (2ms) -> Order Service (15ms) -> DB (120ms)"

  relationship: |
    Metrics tell you SOMETHING is wrong (alert fires)
    Logs tell you WHAT went wrong (error details)
    Traces tell you WHERE it went wrong (which service/call)
```

## Logging
```
logging:

  log_levels:
    TRACE: "Very detailed, step-by-step execution (rarely used in production)"
    DEBUG: "Detailed diagnostic info for developers"
    INFO: "Normal operation events (request received, job completed)"
    WARN: "Unexpected but handled situation (retry succeeded, deprecated API used)"
    ERROR: "Operation failed, needs attention (DB connection lost, API call failed)"
    FATAL: "Application cannot continue, shutting down"

    production_level: "INFO and above (DEBUG/TRACE generate too much volume)"
    debugging_level: "Temporarily enable DEBUG for specific services"

  structured_logging:
    description: |
      Log entries as key-value pairs (JSON) instead of free-form text.
      Makes logs searchable, filterable, and parseable by machines.

    unstructured_bad: |
      [2026-03-30 10:15:30] ERROR: Failed to process order 123 for user 456, timeout after 5s

    structured_good: |
      {
        "timestamp": "2026-03-30T10:15:30Z",
        "level": "ERROR",
        "message": "failed to process order",
        "order_id": "123",
        "user_id": "456",
        "error": "timeout after 5s",
        "service": "order-service",
        "trace_id": "abc-def-123",
        "duration_ms": 5000
      }

    why_structured:
      - "Search by field: order_id=123"
      - "Filter by level: level=ERROR"
      - "Correlate across services: trace_id=abc-def-123"
      - "Build dashboards from log data"
      - "Set up alerts on specific field values"

  what_to_log:
    always:
      - "Request received (method, path, user agent)"
      - "Request completed (status code, duration)"
      - "Errors with full context (what failed, input data, stack trace)"
      - "Authentication events (login, logout, failed attempts)"
      - "External service calls (target, duration, result)"
    never:
      - "Passwords, tokens, API keys"
      - "Full credit card numbers, SSNs"
      - "Personal data unless needed (GDPR compliance)"
      - "Health check requests (too noisy)"

  correlation_id:
    description: Unique ID that follows a request across all services
    also_called: Request ID, Trace ID
    how: |
      1. API Gateway generates X-Request-ID header
      2. Every service includes it in all log entries
      3. Search logs by this ID to see full request flow
    example: "All log entries with trace_id=abc-def-123 show the complete journey"
```

## ELK Stack
```
elk_stack:
  description: |
    Popular log aggregation and analysis platform.
    ELK = Elasticsearch + Logstash + Kibana

  components:
    elasticsearch:
      role: Store and search logs
      type: Distributed search engine
      features:
        - Full-text search across billions of log entries
        - Index-based storage (one index per day typically)
        - Aggregations for dashboards and analytics

    logstash:
      role: Collect, transform, and forward logs
      type: Data processing pipeline
      features:
        - Input plugins (file, syslog, Kafka, beats)
        - Filter plugins (grok, mutate, geoip)
        - Output plugins (Elasticsearch, S3, Kafka)

    kibana:
      role: Visualize and explore logs
      type: Web UI dashboard
      features:
        - Search and filter logs
        - Build dashboards and visualizations
        - Create alerts
        - Discover patterns

    beats:
      role: Lightweight data shippers (often replaces Logstash for collection)
      types:
        filebeat: "Ship log files"
        metricbeat: "Ship system/service metrics"
        packetbeat: "Ship network data"

  modern_alternatives:
    loki: "Grafana Loki - like Prometheus but for logs (label-based, cheaper)"
    datadog: "Managed observability platform"
    splunk: "Enterprise log analytics"

  typical_flow: |
    Application -> stdout -> Filebeat -> Elasticsearch -> Kibana
    Application -> stdout -> Fluentd -> Elasticsearch -> Kibana (K8s common)
```

## Metrics with Prometheus + Grafana
```
prometheus:
  description: |
    Open-source monitoring system that collects metrics via pull model.
    Most popular metrics solution for cloud-native applications.

  how_it_works: |
    1. Application exposes /metrics endpoint (Prometheus format)
    2. Prometheus scrapes /metrics at regular intervals (e.g., 15s)
    3. Prometheus stores time-series data locally
    4. Grafana queries Prometheus to build dashboards
    5. Alertmanager fires alerts based on Prometheus rules

  metric_types:
    counter:
      description: Monotonically increasing value (only goes up, resets on restart)
      use_for: "Total requests, total errors, bytes transferred"
      example: "http_requests_total{method=GET, status=200} = 15432"

    gauge:
      description: Value that can go up or down
      use_for: "Current connections, memory usage, temperature, queue size"
      example: "active_connections = 42"

    histogram:
      description: Samples observations and counts them in configurable buckets
      use_for: "Request duration, response size"
      example: "http_request_duration_seconds_bucket{le=0.1} = 5000"
      note: "Allows calculating percentiles (p50, p95, p99)"

    summary:
      description: Similar to histogram but calculates quantiles on client side
      use_for: "When you need exact quantiles, not bucket approximations"
      note: "Cannot aggregate across instances (prefer histograms)"

  key_metrics_to_track:
    RED_method:
      description: For request-driven services
      rate: "Requests per second"
      errors: "Number of failed requests per second"
      duration: "Distribution of request latencies"

    USE_method:
      description: For resources (CPU, memory, disk)
      utilization: "Percentage of resource being used"
      saturation: "Amount of work queued (waiting)"
      errors: "Number of error events"

    four_golden_signals:
      description: Google SRE's key metrics
      latency: "Time to serve a request"
      traffic: "Requests per second"
      errors: "Rate of failed requests"
      saturation: "How full is the service (CPU, memory, queue depth)"

grafana:
  description: Visualization and dashboarding tool
  features:
    - "Query multiple data sources (Prometheus, Elasticsearch, Loki)"
    - "Build dashboards with graphs, tables, heatmaps"
    - "Set up alerts with notification channels (Slack, PagerDuty)"
    - "Template variables for dynamic dashboards"
    - "Dashboard as code (JSON, Terraform)"
```

## Distributed Tracing
```
distributed_tracing:
  description: |
    Track a single request as it flows through multiple services.
    Each service adds a "span" to the trace, showing timing and metadata.

  concepts:
    trace: "The entire journey of a request (collection of spans)"
    span: "A single unit of work (one service call, one DB query)"
    parent_span: "The span that initiated a child span"
    trace_id: "Unique ID for the entire trace (propagated across services)"
    span_id: "Unique ID for each individual span"

  example_trace:
    trace_id: "abc-123"
    spans:
      - "API Gateway: 200ms (parent)"
      - "  Auth Service: 10ms"
      - "  Order Service: 180ms"
      - "    Database Query: 45ms"
      - "    Payment Service (gRPC): 120ms"
      - "      Stripe API: 95ms"
      - "    Cache Read: 2ms"

  tools:
    jaeger:
      by: Uber (now CNCF)
      features:
        - "Distributed context propagation"
        - "Service dependency analysis"
        - "Root cause analysis"
        - "Performance/latency optimization"
      storage: "Elasticsearch, Cassandra, Kafka"

    zipkin:
      by: Twitter
      features:
        - "Similar to Jaeger"
        - "Simpler setup"
        - "Good for smaller deployments"

    opentelemetry:
      description: |
        Vendor-neutral standard for collecting telemetry data
        (traces, metrics, logs). The future of observability instrumentation.
      key_points:
        - "Single SDK for traces + metrics + logs"
        - "Vendor agnostic: export to Jaeger, Zipkin, Datadog, etc."
        - "Auto-instrumentation for common libraries"
        - "CNCF project, industry standard"
      components:
        sdk: "Instrument your code"
        collector: "Receive, process, and export telemetry data"
        exporters: "Send to backend (Jaeger, Prometheus, OTLP)"

  context_propagation:
    description: How trace context is passed between services
    headers:
      w3c_traceparent: "traceparent: 00-<trace-id>-<span-id>-<flags>"
      b3_zipkin: "X-B3-TraceId, X-B3-SpanId, X-B3-ParentSpanId"
      jaeger: "uber-trace-id: {trace-id}:{span-id}:{parent-id}:{flags}"
    recommendation: "Use W3C Trace Context (standard, supported by all)"
```

## Alerting
```
alerting:
  description: Automatically notify teams when something goes wrong

  alert_design:
    good_alert:
      - "Actionable: someone can do something about it"
      - "Urgent: needs attention now (not informational)"
      - "Clear: describes what is wrong and where"
      - "Includes runbook link or fix instructions"
    bad_alert:
      - "Flapping: fires and resolves repeatedly"
      - "Too sensitive: fires on minor blips"
      - "Not actionable: nobody knows what to do"
      - "Too many: alert fatigue leads to ignoring all alerts"

  alert_levels:
    critical:
      description: "System is down or major feature broken"
      action: "Page on-call immediately (PagerDuty, Opsgenie)"
      example: "Error rate > 5% for 5 minutes"
    warning:
      description: "Something is degraded but not broken"
      action: "Slack notification, investigate during business hours"
      example: "P95 latency > 2s for 10 minutes"
    info:
      description: "Notable event, no action needed"
      action: "Log, review in daily standup"
      example: "Deployment completed, cache hit rate dropped"

  prometheus_alert_example: |
    groups:
      - name: http_alerts
        rules:
          - alert: HighErrorRate
            expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "High HTTP error rate on {{ $labels.instance }}"
              description: "Error rate is {{ $value | humanizePercentage }} for 5 minutes"
              runbook_url: "https://wiki.example.com/runbooks/high-error-rate"

          - alert: HighLatency
            expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
            for: 10m
            labels:
              severity: warning
            annotations:
              summary: "High P95 latency on {{ $labels.instance }}"

  notification_channels:
    - "PagerDuty / Opsgenie (critical - pages on-call)"
    - "Slack / Teams (warning - team channel)"
    - "Email (info - daily digest)"
    - "Webhook (custom integrations)"
```

## Example - Go Structured Logging with slog
```go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "time"
)

// Middleware that adds request context to logs
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // Create request-scoped logger with correlation fields
        requestID := r.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = generateID() // implement your own
        }

        logger := slog.With(
            "request_id", requestID,
            "method", r.Method,
            "path", r.URL.Path,
            "remote_addr", r.RemoteAddr,
            "user_agent", r.UserAgent(),
        )

        // Add logger to context
        ctx := context.WithValue(r.Context(), "logger", logger)

        // Wrap response writer to capture status code
        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

        logger.Info("request started")
        next.ServeHTTP(wrapped, r.WithContext(ctx))

        logger.Info("request completed",
            "status", wrapped.statusCode,
            "duration_ms", time.Since(start).Milliseconds(),
        )
    })
}

type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}

// Get logger from context
func loggerFromCtx(ctx context.Context) *slog.Logger {
    if logger, ok := ctx.Value("logger").(*slog.Logger); ok {
        return logger
    }
    return slog.Default()
}

func generateID() string {
    return "req-" + time.Now().Format("20060102150405.000")
}

// Handler example using structured logging
func orderHandler(w http.ResponseWriter, r *http.Request) {
    logger := loggerFromCtx(r.Context())

    orderID := r.URL.Query().Get("id")
    logger = logger.With("order_id", orderID)

    logger.Info("fetching order from database")

    // Simulate work
    time.Sleep(50 * time.Millisecond)

    // Log different levels
    logger.Debug("cache miss, querying database")
    logger.Info("order fetched successfully", "items", 3, "total", 99.99)
    // logger.Warn("deprecated API version used", "version", "v1")
    // logger.Error("failed to fetch order", "error", err)

    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"order_id": "` + orderID + `", "status": "completed"}`))
}

func main() {
    // JSON structured logging for production
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
        // Add source file info to logs
        AddSource: true,
    }))
    slog.SetDefault(logger)

    // Add global fields (service name, version, environment)
    slog.SetDefault(logger.With(
        "service", "order-service",
        "version", "1.2.3",
        "env", os.Getenv("APP_ENV"),
    ))

    mux := http.NewServeMux()
    mux.HandleFunc("/api/orders", orderHandler)

    handler := loggingMiddleware(mux)
    slog.Info("server starting", "port", 8080)
    http.ListenAndServe(":8080", handler)
}

// Output (JSON, one line per log entry):
// {"time":"2026-03-30T10:15:30Z","level":"INFO","msg":"request started",
//  "service":"order-service","request_id":"req-123","method":"GET",
//  "path":"/api/orders","remote_addr":"192.168.1.1"}
// {"time":"2026-03-30T10:15:30Z","level":"INFO","msg":"order fetched successfully",
//  "service":"order-service","request_id":"req-123","order_id":"456",
//  "items":3,"total":99.99}
```

## Example - Prometheus Metrics in Go
```go
package main

import (
    "math/rand"
    "net/http"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "path", "status"},
    )

    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration in seconds",
            Buckets: []float64{0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5},
        },
        []string{"method", "path"},
    )

    activeConnections = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_connections",
            Help: "Number of active connections",
        },
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpRequestDuration)
    prometheus.MustRegister(activeConnections)
}

func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        activeConnections.Inc()
        defer activeConnections.Dec()

        wrapped := &statusWriter{ResponseWriter: w, statusCode: 200}
        next.ServeHTTP(wrapped, r)

        duration := time.Since(start).Seconds()
        httpRequestsTotal.WithLabelValues(r.Method, r.URL.Path, http.StatusText(wrapped.statusCode)).Inc()
        httpRequestDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration)
    })
}

type statusWriter struct {
    http.ResponseWriter
    statusCode int
}

func (w *statusWriter) WriteHeader(code int) {
    w.statusCode = code
    w.ResponseWriter.WriteHeader(code)
}

func main() {
    mux := http.NewServeMux()

    // Application routes
    mux.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
        time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
        w.Write([]byte(`{"users": []}`))
    })

    // Prometheus metrics endpoint (scraped by Prometheus)
    mux.Handle("/metrics", promhttp.Handler())

    handler := metricsMiddleware(mux)
    http.ListenAndServe(":8080", handler)
}

// Prometheus scrape config (prometheus.yml):
// scrape_configs:
//   - job_name: 'myapp'
//     scrape_interval: 15s
//     static_configs:
//       - targets: ['localhost:8080']
```

## Example - OpenTelemetry Tracing in Go
```go
package main

import (
    "context"
    "log"
    "net/http"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
    "go.opentelemetry.io/otel/trace"
)

var tracer trace.Tracer

func initTracer() func() {
    ctx := context.Background()

    exporter, err := otlptracehttp.New(ctx,
        otlptracehttp.WithEndpoint("localhost:4318"),
        otlptracehttp.WithInsecure(),
    )
    if err != nil {
        log.Fatal(err)
    }

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName("order-service"),
            semconv.ServiceVersion("1.0.0"),
            attribute.String("environment", "production"),
        )),
    )

    otel.SetTracerProvider(tp)
    tracer = tp.Tracer("order-service")

    return func() { tp.Shutdown(ctx) }
}

func orderHandler(w http.ResponseWriter, r *http.Request) {
    // Start a span for this handler
    ctx, span := tracer.Start(r.Context(), "orderHandler",
        trace.WithAttributes(
            attribute.String("order.id", r.URL.Query().Get("id")),
        ),
    )
    defer span.End()

    // Call database (child span)
    order, err := fetchOrderFromDB(ctx, r.URL.Query().Get("id"))
    if err != nil {
        span.RecordError(err)
        http.Error(w, "internal error", 500)
        return
    }

    // Call payment service (child span)
    _ = callPaymentService(ctx, order)

    w.Write([]byte(`{"status": "ok"}`))
}

func fetchOrderFromDB(ctx context.Context, id string) (string, error) {
    _, span := tracer.Start(ctx, "fetchOrderFromDB",
        trace.WithAttributes(attribute.String("db.system", "postgresql")),
    )
    defer span.End()

    // Simulate DB query
    time.Sleep(45 * time.Millisecond)
    span.SetAttributes(attribute.Int("db.rows_affected", 1))

    return "order-data", nil
}

func callPaymentService(ctx context.Context, order string) error {
    _, span := tracer.Start(ctx, "callPaymentService",
        trace.WithAttributes(attribute.String("rpc.system", "grpc")),
    )
    defer span.End()

    // Simulate gRPC call
    time.Sleep(120 * time.Millisecond)
    return nil
}

func main() {
    cleanup := initTracer()
    defer cleanup()

    http.HandleFunc("/api/orders", orderHandler)
    log.Println("Server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

## Health Check Endpoints
```
health_checks:
  description: |
    Endpoints that report service health status.
    Used by load balancers, Kubernetes, and monitoring tools.

  types:
    liveness:
      path: "/healthz or /livez"
      purpose: "Is the process alive and not deadlocked?"
      checks: "Minimal - just return 200 OK"
      failure_action: "Restart the process (K8s kills the pod)"
      dont_check: "External dependencies (DB, Redis)"

    readiness:
      path: "/readyz or /ready"
      purpose: "Is the service ready to accept traffic?"
      checks: "Database connection, cache connection, startup complete"
      failure_action: "Remove from load balancer (stop sending traffic)"
      when_not_ready: "During startup, during graceful shutdown"

    detailed:
      path: "/health"
      purpose: "Full health status for monitoring dashboards"
      checks: "All dependencies with individual status"
      response: |
        {
          "status": "healthy",
          "checks": {
            "database": {"status": "ok", "latency_ms": 5},
            "redis": {"status": "ok", "latency_ms": 1},
            "kafka": {"status": "degraded", "message": "1 of 3 brokers down"}
          },
          "version": "1.2.3",
          "uptime": "72h15m"
        }
      warning: "Don't expose sensitive info (connection strings, internal IPs)"
```

## Best Practices
```
best_practices:
  logging:
    - "Always use structured logging (JSON) in production"
    - "Include correlation/request ID in every log entry"
    - "Log at appropriate levels (don't overuse ERROR)"
    - "Never log sensitive data (passwords, tokens, PII)"
    - "Write logs to stdout/stderr, let infrastructure handle aggregation"
    - "Include service name, version, and environment in every log"

  metrics:
    - "Follow RED method for services (Rate, Errors, Duration)"
    - "Follow USE method for resources (Utilization, Saturation, Errors)"
    - "Use histograms for latency (not averages - p95/p99 matter)"
    - "Keep cardinality low (don't use user_id as a label)"
    - "Name metrics consistently: http_requests_total, db_query_duration_seconds"

  tracing:
    - "Instrument all inter-service calls"
    - "Propagate trace context through HTTP headers"
    - "Add meaningful attributes to spans (user_id, order_id)"
    - "Use sampling in production (don't trace 100% of requests)"
    - "Use OpenTelemetry for vendor-neutral instrumentation"

  alerting:
    - "Alert on symptoms (high error rate) not causes (CPU high)"
    - "Every alert must be actionable"
    - "Include runbook link in alert annotations"
    - "Use warning -> critical escalation"
    - "Review and prune alerts quarterly (fight alert fatigue)"

  general:
    - "Centralize all observability data (don't SSH into servers to check logs)"
    - "Create dashboards for every service (RED metrics at minimum)"
    - "Set up on-call rotation with clear escalation policy"
    - "Practice incident response (game days, chaos engineering)"
    - "Correlate logs, metrics, and traces using common IDs"
```

## Tags
```
tags:
  - monitoring
  - logging
  - observability
  - prometheus
  - grafana
  - opentelemetry
  - system-design
```
