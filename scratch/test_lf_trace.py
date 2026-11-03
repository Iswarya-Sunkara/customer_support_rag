import os
from pathlib import Path
from langfuse import Langfuse

env_file = Path('.env')
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

pk = os.getenv('LANGFUSE_PUBLIC_KEY', '').strip()
sk = os.getenv('LANGFUSE_SECRET_KEY', '').strip()
host = os.getenv('LANGFUSE_BASE_URL', '').strip()

lf = Langfuse(public_key=pk, secret_key=sk, host=host)

print("Starting observation with end()...")
span = lf.start_observation(
    name="customer_support_rag_query",
    as_type="span",
    input={"question": "How do I fix credit card error 51?"},
    output={"answer": "Check with bank or update card details."},
    metadata={"test": "live_cloud_trace_test", "trace_id": "test_001"}
)
print("Span created:", span)
span.end()
print("Span ended.")
lf.flush()
print("Flushed! Check Langfuse now.")
