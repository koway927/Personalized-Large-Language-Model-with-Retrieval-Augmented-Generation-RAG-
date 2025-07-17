from sentence_transformers import SentenceTransformer
import torch


embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return embedder
    
def embed(info):
    model_embedder = get_embedder()
    # embed with SentenceTransformers
    embedding = model_embedder.encode(info, convert_to_tensor=True)
    # normalize for lance_db with L2
    embedding = torch.nn.functional.normalize(embedding, p=2, dim=0).tolist()
    return embedding    
