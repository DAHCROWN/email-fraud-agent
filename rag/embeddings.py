# rag/embeddings.py

from typing import List
from google.cloud import aiplatform

class EmbeddingEngine:
    """
    Embedding interface powered by Vertex AI embeddings.
    """

    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        aiplatform.init()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Vertex AI embeddings model.
        """
        from google.cloud import aiplatform

        model = aiplatform.TextEmbeddingModel.from_pretrained(self.model_name)
        response = model.get_embeddings(texts)

        return [emb.values for emb in response]