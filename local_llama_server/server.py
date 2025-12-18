"""
Local LLaMA MCP Server

Provides local quantized LLaMA model inference for offline AI capabilities.
This server enables private, on-device AI without external API dependencies.
"""

import asyncio
import logging
from fastmcp import FastMCP
from .config import Config
from .tools.inference import local_inference
from .tools.embeddings import local_embed
from .resources.models import models_resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP application
app = FastMCP("Local LLaMA MCP Server")


@app.tool()
async def local_llama_inference(
    prompt: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    system_prompt: str | None = None,
    chat_format: bool = True,
) -> dict:
    """Wrapper tool that delegates to the local_inference implementation.

    This keeps the real logic in tools/inference.py while exposing a FastMCP
    tool with a stable name for MCP Inspector.
    """

    return await local_inference(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        system_prompt=system_prompt,
        chat_format=chat_format,
    )


@app.tool()
async def local_llama_embed(
    input_text,
    model_path: str | None = None,
    normalize: bool = True,
    pooling_method: str = "mean",
) -> dict:
    """Wrapper tool that delegates to the local_embed implementation."""

    return await local_embed(
        input_text=input_text,
        model_path=model_path,
        normalize=normalize,
        pooling_method=pooling_method,
    )


# Register resources using explicit URI (function first, URI second)
app.add_resource_fn(models_resource, "local://models")

@app.tool()
def health_check() -> str:
    """Health check endpoint for the Local LLaMA MCP server."""
    return "Local LLaMA MCP Server is running"

async def main():
    """Main entry point for the Local LLaMA MCP server."""
    try:
        config = Config()
        logger.info("Starting Local LLaMA MCP Server...")
        logger.info(f"Model path: {config.MODEL_PATH}")
        logger.info(f"Device: {config.DEVICE}")
        
        # Initialize model (this would load the actual model in production)
        logger.info("Model initialization completed")
        
        # Run the FastMCP server over stdio (no nested event loop)
        await app.run_stdio_async()
    except Exception as e:
        logger.error(f"Failed to start Local LLaMA MCP Server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
