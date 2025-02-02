from langfuse.llama_index import LlamaIndexInstrumentor
from api.config.settings import settings

instrumentor = LlamaIndexInstrumentor(
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    secret_key=settings.LANGFUSE_SECRET_KEY,
    host=settings.LANGFUSE_HOST,
)

# Start tracing
instrumentor.start()
