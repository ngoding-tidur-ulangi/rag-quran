from dotenv import load_dotenv
import os
import faiss
import pandas as pd
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
port = int(os.getenv("PORT", 7860))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL"), cache_folder="/app/cache")
model = genai.GenerativeModel(os.getenv("LLM_MODEL"))

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define file paths
FAISS_INDEX_PATH = "faiss_index.bin"
DATA_AUGMENTED_PATH = "The Quran Dataset Augmented.csv"

# Load FAISS index
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
else:
    raise FileNotFoundError(f"FAISS index file '{FAISS_INDEX_PATH}' not found!")

# Load augmented dataset
if os.path.exists(DATA_AUGMENTED_PATH):
    dataAugmented = pd.read_csv(DATA_AUGMENTED_PATH)
else:
    raise FileNotFoundError(f"Data Augmented file '{DATA_AUGMENTED_PATH}' not found!")

# Define request model
class QueryRequest(BaseModel):
    query: str
    history: list[dict]

# Function to retrieve relevant documents
def get_relevant_docs(query, top_k=10):
    query_vector = embedding_model.encode(query).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    filtered_indices = [indices[0][i] for i in range(len(indices[0])) if distances[0][i] > 0.2]

    if not filtered_indices:
        return pd.DataFrame()

    retrieved_data = [dataAugmented.iloc[i] for i in filtered_indices if i < len(dataAugmented)]
    retrieved_data_df = pd.DataFrame(retrieved_data)

    def remove_subsets(group):
        filtered_rows = []
        selected_rows = []

        group = group.sort_values(['first_ayah_no_surah', 'last_ayah_no_surah'], ascending=[True, False]).reset_index(drop=True)

        for _, row in group.iterrows():
            first, last = row['first_ayah_no_surah'], row['last_ayah_no_surah']
            if any(f <= first and l >= last for f, l in filtered_rows):
                continue
            filtered_rows.append((first, last))
            selected_rows.append(row)

        return pd.DataFrame(selected_rows)

    df_filtered = retrieved_data_df.groupby('surah_no', group_keys=False).apply(remove_subsets).reset_index(drop=True)
    return df_filtered

# Function to generate response
def generate_response(query, retrieved_docs, history):
    context = "\n\n".join(retrieved_docs)
    history_string = "".join(f"{entry['messager']}: {entry['message']}\n" for entry in history)[-10000:]

    prompt = f"""
        Role: You are an Islamic scholar answering a question about the Quran.
        Goal: Answer the following query based on the retrieved ayah (translated in English) and the chat history.
        Retrieved Ayah: {context}
        History: {history_string}
        Query: {query}
        Answer:
    """

    response = model.generate_content(prompt)
    return response.text if response else "No response generated."

# API endpoint
@app.post("/rag")
def rag_query(request: QueryRequest):
    query, history = request.query, request.history

    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")
    
    if history is None:
        raise HTTPException(status_code=400, detail="Missing history parameter")

    retrieved_docs = get_relevant_docs(query)
    if retrieved_docs.empty:
        return {"response": "No relevant documents found."}

    response_text = generate_response(query, retrieved_docs["ayah_en"].tolist(), history)

    return {
        "query": query,
        "retrieved_docs": retrieved_docs.to_dict(orient='records'),
        "response": response_text
    }

@app.get("/")
def greet_json():
    return {"Hello": "World!"}