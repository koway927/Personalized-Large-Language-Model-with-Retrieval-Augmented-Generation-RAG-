import lancedb
from sentence_transformers import SentenceTransformer

# Initialize the embedder and database connection
embedder = SentenceTransformer("all-MiniLM-L6-v2")
db = lancedb.connect("db")

def delete_existing_tables():
    """
    Deletes all existing tables in the LanceDB database.
    """
    try:
        for table_name in db.table_names():
            print(f"Dropped table: {table_name}")
    except Exception as e:
        print("Error deleting tables:", e)

def setup_tables():
    try:
        # Delete existing tables
        delete_existing_tables()

        # Example data for sessions
        example_sessions = [
            {
                "session_id": 1,
                "user_id": "1",
                "prompt_answer": "Q: Who invented the plane? A: The Wright Brothers \n Q: When was it invented? A: 1903"
            },
            {
                "session_id": 2,
                "user_id": "1",
                "prompt_answer": "Q: When was 9/11? A: September 11, 2001 \n Q: Who did it? A: Al-Qaeda"
            }
        ]

        # Example data for personal info
        example_personal_info = [
            {
                "user_id": "1",
                "info_chunk": "user is interested in planes",
                "info_chunk_embedding": embedder.encode("user is interested in planes", convert_to_tensor=True).tolist()
            }
        ]

        # Set up the "sessions" table
        session_table = db.create_table("sessions", data=example_sessions)

        # Set up the "personal_info" table
        personal_table = db.create_table("personal_info", data=example_personal_info)

        # Print the contents of the tables for verification
        print("Tables in DB:", db.table_names())
        for table_name in db.table_names():
            table = db.open_table(table_name)
            print(f"\n--- Contents of table: {table_name} ---")
            print(table.to_pandas())

    except Exception as e:
        print("Error setting up tables:", e)

# Call the setup function
setup_tables()