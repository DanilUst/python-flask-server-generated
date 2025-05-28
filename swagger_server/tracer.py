# swagger_server/tracer.py
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# === Инициализируем трассировщик сразу при импорте ===
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": "python-api"}))
)
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4321", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(
    otlp_exporter))


def configure_tracing(app):
    # лишь инструментируем Flask (Connexon)
    FlaskInstrumentor().instrument_app(app.app)
