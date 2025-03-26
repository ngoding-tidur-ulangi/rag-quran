import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os
import zipfile
import gc

# modelEmbedding = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

zip_index = "faiss_index.zip"
zip_data = "The Quran Dataset Augmented.zip"
# csv_path = "The Quran Dataset Augmented.csv"

if os.path.exists(zip_index):
    with zipfile.ZipFile(zip_index, 'r') as zip_ref:
        zip_ref.extractall(".")

if os.path.exists(zip_data):
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        zip_ref.extractall(".")

# if not os.path.exists(csv_path):
#     raise FileNotFoundError(f"{csv_path} not found after extraction!")

# df = pd.read_csv(csv_path)

# def augment_data(group):
#     augmented_data = []
#     for i in range(1, 11):
#         for j in range(len(group)-i):
#             ayah_ens = ""
#             for k in range(j, j+i+1):
#                 ayah_ens += group.iloc[k]["ayah_en"]
#                 if k != j+i:
#                     ayah_ens += " "
#             augmented_data.append({
#                 "surah_no": group.iloc[j]["surah_no"],
#                 "ayah_no_surah": f"{group.iloc[j]['ayah_no_surah']}-{group.iloc[j+i]['ayah_no_surah']}",
#                 "ayah_en": ayah_ens
#             })
#     return pd.DataFrame(augmented_data)

# df_augmented = df.groupby("surah_no", group_keys=False).apply(augment_data)
# df_augmented.head()

# df_final = pd.concat([df[["surah_no", "ayah_no_surah", "ayah_en"]], df_augmented]).sort_values(by=["surah_no", "ayah_no_surah"]).reset_index(drop=True)

# del df
# del df_augmented
# gc.collect() 

# embeddings = []

# for ayah in tqdm(df_final["ayah_en"].tolist(), desc="Encoding embeddings", unit="ayah"):
#     embeddings.append(modelEmbedding.encode(ayah, convert_to_numpy=True))

# embeddings = np.array(embeddings)
# dimension = embeddings.shape[1] 
# index = faiss.IndexFlatIP(dimension)

# index.add(embeddings)

# faiss.write_index(index, "faiss_index.bin")