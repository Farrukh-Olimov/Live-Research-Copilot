// ===== OTLP Receiver =====
otelcol.receiver.otlp "default" {
  grpc {}
  http {}
}

// ===== Processors =====
otelcol.processor.batch "default" {}

// ===== Loki Export =====
loki.write "loki" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

otelcol.exporter.loki "logs" {
  forward_to = [loki.write.loki.receiver]
}

// ===== Tempo Export =====
otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "http://tempo:4317"
    tls {
      insecure = true
    }
  }
}

// ===== Pipelines =====
otelcol.service "default" {
  pipelines {
    logs = {
      receivers  = [otelcol.receiver.otlp.default]
      processors = [otelcol.processor.batch.default]
      exporters  = [otelcol.exporter.loki.logs]
    }

    traces = {
      receivers  = [otelcol.receiver.otlp.default]
      processors = [otelcol.processor.batch.default]
      exporters  = [otelcol.exporter.otlp.tempo]
    }
  }
}