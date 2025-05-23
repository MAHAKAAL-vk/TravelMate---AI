#Jina_embeddings.py
import os
import requests
from typing import List
from dotenv import load_dotenv
from backend.embeddings.Base_embeddings import BaseEmbedding, EmbeddingInput

load_dotenv()

class JinaEmbeddingInput(EmbeddingInput):
    task: str = "text-matching"
    late_chunking: bool = False
    URL: str = "https://api.jina.ai/v1/embeddings"
    headers: dict[str, str] = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("JINA_API_KEY")}'
    }

class JinaEmbedding(BaseEmbedding):
    def __init__(self, embedding_input: JinaEmbeddingInput) -> None:
        super().__init__(embedding_input)

    def _call_embedding_model(self, texts: List[str]) -> List[List[float]]:
        data = {
            "model": self._input.model_name,
            "task": self._input.task,
            "late_chunking": self._input.late_chunking,
            "dimensions": self._input.dimensions,
            "embedding_type": self._input.embedding_type,
            "input": texts
        }

        response = requests.post(self._input.URL, headers=self._input.headers, json=data)

        try:
            response_json = response.json()
        except Exception as e:
            raise ValueError(f"Failed to parse response as JSON: {e}\nRaw response: {response.text}")

        # Log response for debugging
        # print("Jina API raw response:", response_json)

        return self._parse_jina_response(response_json)

    def _parse_jina_response(self, response: dict) -> List[List[float]]:
        if 'data' not in response:
            raise KeyError(f"Missing 'data' in response. Full response: {response}")
        
        result = []
        for embedding in response['data']:
            result.append(embedding['embedding'])
        return result

# if __name__ == "__main__":
#     input = JinaEmbeddingInput(
#         model_name="jina-embeddings-v3",
#         task="text-matching",
#         late_chunking=False,
#         dimensions=1024,
#         embedding_type="float"
#     )
#     embedding = JinaEmbedding(input)
#     embedding_outputs: List[List[float]] = embedding.generate_batch_embeddings(
#         ["Hello, how are you?", "I am Vikash Kushwaha"]
#     )

#     # Calculate cosine similarity between the two embeddings
#     similarity: float = embedding.calculate_cosine_similarity(embedding_outputs[0], embedding_outputs[1])
#     print(f"Cosine similarity: {similarity}")
