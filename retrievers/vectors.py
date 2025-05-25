from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import SearchRequest, Filter, PointStruct, VectorParams, Distance
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(path="qdrant_data")

def semantic_search(query_text, top_k=3):
    query_vector = model.encode(query_text).tolist()
    results = client.search(
        collection_name="enterprise_docs",
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload for hit in results]
