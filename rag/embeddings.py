# rag/embeddings.py

from typing import List
from pinecone import Pinecone

import os

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_MODEL = "llama-text-embed-v2"  # Pinecone-hosted embedding model


class PineconeEmbeddingEngine:
    """
    Embedding engine using Pinecone's hosted embedding model.
    """

    def __init__(self, model_name: str = PINECONE_MODEL):
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set in environment variables.")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.model_name = model_name

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Pinecone's hosted embedding models.
        """
        response = self.pc.inference.embed(
            model=self.model_name,
            inputs=texts
        )
        return response.embeddings