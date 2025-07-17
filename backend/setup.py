from sentence_transformers import SentenceTransformer
import lancedb
from backend.services.db import register_db, initialize_db
from backend.services.embedder import get_embedder
from backend.services.llm import initialize_llm

db = None
embedder = None
sessions_table = None
personal_table = None
def initialize_system():
    # setup the the database, tables, embedder, and llm
    global db, embedder, sessions_table, personal_table

    db = lancedb.connect("backend/db")
    embedder = get_embedder()
    register_db(db)
    sessions_table, personal_table = initialize_db()
    initialize_llm()
