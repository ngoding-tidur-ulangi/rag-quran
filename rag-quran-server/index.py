from dotenv import load_dotenv
import os
import faiss
import pandas as pd
import google.generativeai as genai
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from flask_cors import CORS

load_dotenv()
port = int(os.environ.get("PORT", 5000))
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
FAISS_INDEX_PATH = "faiss_index.bin"
DATA_AUGMENTED_PATH = "The Quran Dataset Augmented.csv"
DATA_PATH = "The Quran Dataset.csv"
VECTOR_DIM = 384 

if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
else:
    raise FileNotFoundError(f"FAISS index file '{FAISS_INDEX_PATH}' not found!")

if os.path.exists(DATA_AUGMENTED_PATH):
    dataAugmented = pd.read_csv(DATA_AUGMENTED_PATH)
else:
    raise FileNotFoundError(f"Data Augmented file '{DATA_AUGMENTED_PATH}' not found!")

# if os.path.exists(DATA_PATH):
#     data = pd.read_csv(DATA_PATH)
# else:
#     raise FileNotFoundError(f"Data file '{DATA_PATH}' not found!")

embedding_model = SentenceTransformer(os.environ.get("EMBEDDING_MODEL"))
model = genai.GenerativeModel(os.environ.get("LLM_MODEL"))



def get_relevant_docs(query, top_k=10):
    query_vector = embedding_model.encode(query).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    filtered_indices = [indices[0][i] for i in range(len(indices[0])) if distances[0][i] > 0.2]

    if filtered_indices == []:
        return pd.DataFrame()

    retrieved_data = [dataAugmented.iloc[i] for i in filtered_indices if i < len(dataAugmented)]

    retrieved_data_df = pd.DataFrame(retrieved_data)

    def remove_subsets(group):
        filtered_rows = []
        selected_rows = []

        group = group.sort_values(['first_ayah_no_surah', 'last_ayah_no_surah'], ascending=[True, False]).reset_index(drop=True)

        for i, row in group.iterrows():
            first, last = row['first_ayah_no_surah'], row['last_ayah_no_surah']
            
            if any(f <= first and l >= last for f, l in filtered_rows):
                continue
            
            filtered_rows.append((first, last))
            selected_rows.append(row)

        return pd.DataFrame(selected_rows)

    df_filtered = retrieved_data_df.groupby('surah_no', group_keys=False).apply(remove_subsets).reset_index(drop=True)

    return df_filtered


def generate_response(query, retrieved_docs, history):
    context = "\n\n".join(retrieved_docs)
    historyString = ""
    for entry in history:
        historyString += f"{entry['messager']}: {entry['message']}\n"
    historyString = historyString[-10000:]
    prompt = f"""
        Role: You are an Islamic scholar answering a question about the Quran .
        Goal: Answer the following query based on the retrieved ayah (translated in english) in Quran and the chat history. Answer in the perspective of AGENT that talk to USER in history.
        Retrieved Ayah: {context}
        History: {historyString}
        Query: {query}
        Answer:
    """

    response = model.generate_content(prompt)

    return response.text if response else "No response generated."


@app.route("/rag", methods=["POST"])
def rag_query():
    data = request.json
    query = data.get("query")
    history = data.get("history")

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    
    if history is None:
        return jsonify({"error": "Missing history parameter"}), 400
    
    retrieved_docs = get_relevant_docs(query)
    if retrieved_docs.empty:
        return jsonify({"response": "No relevant documents found."}),
    response = generate_response(query, retrieved_docs["ayah_en"].tolist(), history)

    return jsonify({"query": query, "retrieved_docs": retrieved_docs.to_dict(orient='records'), "response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
