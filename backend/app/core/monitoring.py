from prometheus_client import Counter, Histogram, Gauge

# Count total questions received
REQUEST_COUNT = Counter("agent_requests_total", "Total requests to the AI Agent")

# Track latency of Agent's thinking process
AGENT_LATENCY = Histogram("agent_latency_seconds", "Time spent processing the request")

# Count total errors encountered
ERROR_COUNT = Counter("agent_errors_total", "Total errors in the AI Agent system")

# Measure response length as a proxy for tokens
RESPONSE_LENGTH = Histogram("agent_response_length_chars", "Length of generated answer in characters")

# Track how many documents are retrieved from Milvus per query
RETRIEVED_DOCS_COUNT = Histogram("agent_retrieved_documents_count", "Number of documents retrieved per query")

# Store system information
AGENT_INFO = Gauge("agent_info", "Metadata about the current AI Agent environment", ["app_name", "model"])