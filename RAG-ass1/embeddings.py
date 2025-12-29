# embeddings.py
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        # Fast + high quality
        self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v1")

    def embed(self, texts):
        return self.model.encode(texts).tolist()
