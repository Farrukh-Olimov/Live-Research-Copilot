// ===== Exporters =====
loki.write "loki" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

otelcol.exporter.loki "logs" {
  forward_to = [loki.write.loki.receiver]
}

otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo:4317"
    tls {
      insecure = true
    }
  }
}

otelcol.exporter.prometheus "metrics" {
  forward_to = [prometheus.remote_write.default.receiver]
}

prometheus.remote_write "default" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}

// ===== Pipelines =====

// ---- LOGS ----
otelcol.processor.memory_limiter "logs_mem" {
  check_interval = "1s"
  limit          = "150MiB"   

  output {
    logs = [otelcol.processor.batch.logs.input]
  }
}

otelcol.processor.batch "logs" {
  output {
    logs = [otelcol.exporter.loki.logs.input]
  }
}

// ---- TRACES ----
otelcol.processor.memory_limiter "traces_mem" {
  check_interval = "1s"
  limit          = "150MiB"

  output {
    traces = [otelcol.processor.batch.traces.input]
  }
}

otelcol.processor.batch "traces" {
  output {
    traces = [otelcol.exporter.otlp.tempo.input]
  }
}

// ---- METRICS ----
otelcol.processor.memory_limiter "metrics_mem" {
  check_interval = "1s"
  limit          = "150MiB"

  output {
    metrics = [otelcol.processor.batch.metrics.input]
  }
}

otelcol.processor.batch "metrics" {
  output {
    metrics = [otelcol.exporter.prometheus.metrics.input]
  }
}

// ===== Receiver (single definition) =====
otelcol.receiver.otlp "default" {
  grpc {}
  http {}

  output {
    logs    = [otelcol.processor.memory_limiter.logs_mem.input]
    traces  = [otelcol.processor.memory_limiter.traces_mem.input]
    metrics = [otelcol.processor.memory_limiter.metrics_mem.input]
  }
}