import logging
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

def setup_tracing(app, service_name="senior-ai-agent"):
    # 1. Setup Resource
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    # 2. Setup Tracer
    provider = TracerProvider(resource=resource)
    trace_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
    provider.add_span_processor(trace_processor)
    trace.set_tracer_provider(provider)

    # 3. Setup Logger Provider & OTLP Log Exporter
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    
    log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    
    # Attach OTLP Handler to Python root logger
    otlp_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(otlp_handler)

    # 4. Instrument Logging to include trace_id and span_id in standard formatter
    LoggingInstrumentor().instrument(set_logging_format=True)

    # 5. Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    return trace.get_tracer(__name__)
