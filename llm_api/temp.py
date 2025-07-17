import lancedb
import torch
from sentence_transformers import SentenceTransformer
db = lancedb.connect("db")

sessions_table = db.open_table("sessions")
personal_table = db.open_table("personal_info")
# embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# embedding = embedder.encode("tell me about planes", convert_to_tensor=True)
#     # normalize for lance_db with L2
# embedding = torch.nn.functional.normalize(embedding, p=2, dim=0).tolist()
# personal_info = (
#         personal_table.search(embedding)
#         .where(f"user_id = {1}")
#         .limit(5)
#         .to_pandas()
#     )['info_chunk'].tolist()
# if personal_info:
#     print("found")
# print(personal_info)
print(sessions_table.to_pandas()['history_prompt'].iloc[2])