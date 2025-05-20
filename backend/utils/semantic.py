from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def is_similar_query(query1: str, query2: str, threshold: float = 0.75) -> bool:
    embeddings = model.encode([query1, query2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity > threshold
