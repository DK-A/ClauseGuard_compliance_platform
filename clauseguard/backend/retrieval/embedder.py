from backend.config import get_embedding_model

class Embedder:
    def __init__(self):
        # Fetches fine-tuned model depending on hardware profile
        self.model = get_embedding_model()
        
    def embed_text(self, text: str):
        """
        Embeds a single string and returns a float list.
        """
        return self.model.encode(text)
        
    def embed_batch(self, texts: list):
        """
        Embeds a list of strings and returns a list of float lists.
        """
        return self.model.encode(texts)
