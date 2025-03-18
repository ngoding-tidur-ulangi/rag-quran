import os
import faiss
from sentence_transformers import SentenceTransformer


FAISS_INDEX_PATH = "faiss_index.bin"
VECTOR_DIM = 384

if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
else:
    raise FileNotFoundError(f"FAISS index file '{FAISS_INDEX_PATH}' not found!")

distances, indices = index.search("what is the purpose of life", top_k)

print(distances)

# text = "I am a sentence for which I would like to get its embedding."
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# print(embedding_model.encode(text).shape)