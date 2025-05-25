from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json
import uuid

# Load parsed docs
import os

# Get path to root of project
base_path = os.path.dirname(os.path.dirname(__file__))
parsed_path = os.path.join(base_path, "ingest", "parsed_docs.jsonl")

# Load parsed documents
with open(parsed_path, "r", encoding="utf-8") as f:
    docs = [json.loads(line) for line in f]

# Split long text into smaller chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_chunks = []

for doc in docs:
    chunks = splitter.create_documents([doc["body"]])
    for chunk in chunks:
        all_chunks.append({
            "id": str(uuid.uuid4()),
            "text": chunk.page_content,
            "metadata": {
                "doc_id": doc["doc_id"],
                "source_type": doc["source_type"],
                "title": doc["title"],
                "created_at": doc["created_at"]
            }
        })

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings
texts = [c["text"] for c in all_chunks]
embeddings = model.encode(texts)

# Initialize Qdrant client (local or remote)
client = QdrantClient(path="qdrant_data")  # stores in local directory

# Create a collection if not exists
collection_name = "enterprise_docs"
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=embeddings[0].shape[0], distance=Distance.COSINE),
)

points = [
    PointStruct(
        id=chunk["id"],
        vector=vector.tolist(),
        payload={
            **chunk["metadata"],
            "text": chunk["text"]  # <-- Add this line
        }
    )
    for chunk, vector in zip(all_chunks, embeddings)
]


print("📄 Preview of embedded chunks:")
for chunk in all_chunks[:3]:  # Preview first 3 chunks
    print(f"🔹 From document: {chunk['metadata']['title']}")
    print(f"   Chunk text preview: {chunk['text'][:100]}...\n")

client.upsert(collection_name=collection_name, points=points)

print(f"✅ Indexed {len(points)} document chunks into Qdrant.")
