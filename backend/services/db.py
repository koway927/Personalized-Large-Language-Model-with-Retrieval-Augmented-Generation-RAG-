
import lancedb
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from backend.services.embedder import embed
from datetime import datetime

db = None
sessions_table = None
personal_table = None
'''
Structure - 1 table for storing session/conversation history, 1 table for personal info
Table: Sessions
    Column: session_id -> int
    Column: user_id -> string
    Column: prompt and answer -> text

Table: Personal Info
    Column: user_id -> string
    Column: info_chunk -> text
    Column: vector -> vector embedding
'''

def register_db(db_instance):
    global db
    db = db_instance

# setup vector database - lancedb
def initialize_db():
    # initialize db with values if there is no database or if database is empty
    global sessions_table, personal_table
    example_sessions = [
        {
            "user_id": '1', 
            "session_id": 1,
            "history_prompt": "Q: Who invented the plane? A: The Wright Brothers \n Q: When was it invented? A: 1903"
        },
        {
            "user_id": '1', 
            "session_id": 2,
            "history_prompt": "Q: When was 9/11 A: September 11, 2001 \n Q: Who did it? A: Bush"
        }   
    ]
    example_personal_info = [
        {
            "user_id": '1',
            "info_chunk": "user is interested in planes",
            "vector": embed("user is interested in planes"),
            "tags": ['planes'],
            "usage_count": 0,
            "time_stamp": f"{datetime.now().isoformat()}"
        }
    ]

    # setup tables
    if "sessions" not in db.table_names():
        sessions_table = db.create_table("sessions", data=example_sessions)
    else:
        sessions_table = db.open_table("sessions")

    if "personal_info" not in db.table_names():
        personal_table = db.create_table("personal_info", data=example_personal_info)
    else:
        personal_table = db.open_table("personal_info")

    return sessions_table, personal_table

def save_user_data(data, user_id):
    personal_table = db.open_table("personal_info")
    interests = data.get("interests", [])
    interests_str = ", ".join(interests)
    data_text = f"{data.get('name', '')}, {data.get('email', '')}, {data.get('gender', '')}, {data.get('location', '')}, {data.get('occupation', '')}, {interests_str}"
    # embedding = embedder.encode(data_text, convert_to_tensor=True).tolist()
    embedding = embed(data_text)
    rows = personal_table.to_pandas()
    new_record = {
        "user_id": user_id,
        "info_chunk": data_text,
        "vector": embedding,
        "tags": [],
        "usage_count": 0,
        "time_stamp": f"{datetime.now().isoformat()}"
    }
    existing_record = rows[rows["user_id"] == user_id]
    if existing_record.empty:
        personal_table.add([new_record])
    else:
        personal_table.update(where=f"user_id == '{str(user_id)}'", values={"info_chunk": data_text, "info_chunk_embedding": embedding})
    
    status = "success"
    return status

def save_answer_data(data, user_id):
    personal_table = db.open_table("personal_info")
    answer_data = data.get("answer")
    # embedding = embedder.encode(answer_data, convert_to_tensor=True).tolist()
    embedding = embed(answer_data)
    rows = personal_table.to_pandas()
    new_record = {
        "user_id": user_id,
        "info_chunk": answer_data,
        "vector": embedding,
        "tags": [],
        "usage_count": 0,
        "time_stamp": f"{datetime.now().isoformat()}"
    }
    personal_table.add([new_record])
    status = "success"
    return status

def save_session_data(data):
    session_table = db.open_table("sessions")
    new_record = {
        "session_id": data.get("session_id"),
        "user_id": data.get("user_id"),
        "prompt_answer": data.get("prompt_answer")
    }
    session_table.add([new_record])
    status = "success"
    return status

def get_user_data(user_id):

    personal_table = db.open_table("personal_info")
    rows = personal_table.to_pandas()
    user_data = rows[rows["user_id"] == user_id]
    if user_data.empty:
        return {"status": "error", "message": "User data not found"}
    
    return {"status": "success", "data": user_data.to_dict(orient="records")}


def get_user_answers(user_id):
    personal_table = db.open_table("personal_info")
    rows = personal_table.to_pandas()
    user_answers = rows[rows["user_id"] == user_id]
    if user_answers.empty:
        return {"status": "error", "message": "User answers not found"}
    return {"status": "success", "data": user_answers.to_dict(orient="records")
    }
def get_user_sessions(user_id):

    session_table = db.open_table("sessions")
    rows = session_table.to_pandas()
    user_sessions = rows[rows["user_id"] == user_id]
    if user_sessions.empty:
        return {"status": "error", "message": "User sessions not found"}
    return {"status": "success", "data": user_sessions.to_dict(orient="records")}


# def save_user_data(data, user_id):
#     personal_table = db.open_table("personal_info")
#     interests = data.get("interests", [])
#     interests_str = ", ".join(interests)
#     data_text = f"{data.get('name', '')}, {data.get('email', '')}, {data.get('gender', '')}, {data.get('location', '')}, {data.get('occupation', '')}, {interests_str}"
#     embedding = embedder.encode(data_text, convert_to_tensor=True).tolist()
#     rows = personal_table.to_pandas()
#     new_record = {
#         "user_id": user_id,
#         "info_chunk": data_text,
#         "vector": embedding
#     }
#     personal_table.add([new_record])
#     status = "success"
#     return status

# def save_answer_data(data, user_id):
#     personal_table = db.open_table("personal_info")
#     answer_data = data.get("answer")
#     embedding = embedder.encode(answer_data, convert_to_tensor=True).tolist()
#     rows = personal_table.to_pandas()
#     new_record = {
#         "user_id": user_id,
#         "info_chunk": answer_data,
#         "vector": embedding
#     }
#     personal_table.add([new_record])
#     status = "success"
#     return status




# try:
#     # example data
#     example_sessions = [
#         {
#             "session_id": 1,
#             "user_id": 1, 
#             "prompt_answer": "Q: Who invented the plane? A: The Wright Brothers \n Q: When was it invented? A: 1903"
#         },
#         {
#             "session_id": 2,
#             "user_id": 1, 
#             "prompt_answer": "Q: When was 9/11 A: September 11, 2001 \n Q: Who did it? A: Bush"
#         }
#     ]
#     example_personal_info = [
#         {
#             "user_id": 1,
#             "info_chunk": "user is interested in planes",
#             "vector": embedder.encode("user is interested in planes", convert_to_tensor=True).tolist()
#         }
#     ]
#     # setup tables
#     #if "sessions" not in db.table_names():
#     #    session_table = db.create_table("sessions", data=example_sessions)
#     #else:
#     #    session_table = db.open_table("sessions")
#     #    session_table.add(example_sessions)


#     #if "personal_info" not in db.table_names():
#     #    personal_table = db.create_table("personal_info", data=example_personal_info)
#     #else:
#     #    personal_table = db.open_table("personal_info")
#     #    personal_table.add(example_personal_info)
#     #print("Tables in DB:", db.table_names())
#     for table_name in db.table_names():
#          table = db.open_table(table_name)
#          print(f"\n--- Contents of table: {table_name} ---")
#          print(table.to_pandas())
#     #for table_name in db.table_names():
#     #    table = db.open_table(table_name)
#     #    table.delete(where="true")

    
# except Exception as e:
#     print(e)