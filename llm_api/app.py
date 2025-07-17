from flask import Flask, request
import requests
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import faiss
import lancedb
import torch

app = Flask(__name__)


llm_url = 'http://127.0.0.1:5000/ask'
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# setup vector database - lancedb
'''
Structure - 1 table for storing session/conversation history, 1 table for personal info
Table: Sessions
    Column: session_id -> int
    Column: user_id -> int?
    Column: prompt and answer -> text

Table: Personal Info
    Column: user_id -> int?
    Column: info_chunk -> text
    Column: info_chunk_embedding -> vector embedding
'''
db = lancedb.connect("db")

# example data
example_sessions = [
    {
        "user_id": 1, 
        "session_id": 1,
        "history_prompt": "Q: Who invented the plane? A: The Wright Brothers \n Q: When was it invented? A: 1903"
    },
    {
        "user_id": 1, 
        "session_id": 2,
        "history_prompt": "Q: When was 9/11 A: September 11, 2001 \n Q: Who did it? A: Bush"
    }
]

example_embedding = embedder.encode("user is interested in planes", convert_to_tensor=True)
example_embedding = torch.nn.functional.normalize(example_embedding, p=2, dim=0).tolist()
example_personal_info = [
    {
        "user_id": 1,
        "info_chunk": "user is interested in planes",
        "vector": example_embedding
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


def embed(info):
    embedding = embedder.encode(info, convert_to_tensor=True)
    # normalize for lance_db with L2
    embedding = torch.nn.functional.normalize(embedding, p=2, dim=0).tolist()
    return embedding    


def generate_prompt(query, user_id, session_id):
    '''
    RAG setup for creating and generating prompts 
    '''
    query_embedding = embed(query)
    
    # vector search on personal information filtering by user, retrieve top 5 results
    personal_info = (
        personal_table.search(query_embedding)
        .where(f"user_id = {user_id}")
        .limit(5)
        .to_pandas()
    )['info_chunk'].tolist()

    if personal_info:
        print("Info Found!")
    personal_info = '\n'.join(personal_info) if personal_info else ["(No personal info found)"]

    '''
    future considerations:
        - extract personal information from query beforing performing search
        - extract prompt specific questions and search e.g. prompt is a question -> user likes this type of question
        - change personal_info to include task specific information e.g. questions, formatting, explanations, etc
    '''

    # extract prompt history
    history_prompt = (
        sessions_table.search()
        .where(f"user_id = {user_id} AND session_id = {session_id}")
        .to_pandas()
    )

    # new session
    if history_prompt.empty: 
        full_prompt = (
            f"Additional information about the user and/or the current query {personal_info}\n"
            f"Query: {query}\\n"
            f"Response:"
        )
        # return the prompt, and new history prompt without the answer
        return full_prompt, f"Query: {query}\nResponse:"

    history_prompt = history_prompt['history_prompt'].tolist()
    full_prompt = (
        f"Past Queries and Responses: {history_prompt[0]}\n"
        f"Additional information about the user and/or the current query {personal_info}\n"
        f"Query: {query}"
        f"Response:"
    )
    # return the prompt and updated history prompt without the answer
    return full_prompt, f"{history_prompt[0]}\nQuery: {query}\nResponse:"

@app.route('/query-llm', methods=['POST'])
def query():
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    query = data.get("query")

    prompt, history_prompt = generate_prompt(query, user_id, session_id)
    
    payload = {
        "user_id": user_id,
        "prompt": prompt
    }
    response = requests.post(llm_url, json=payload).json().get('response')
    print(response)

    # add the response to the history response
    session = [
        {
            "session_id": session_id,
            "user_id": user_id, 
            "history_prompt": f"{history_prompt} {response}"
        }
    ]

    # update session_table with new history prompt
    # DOES NOT DELETE FROM DISK, update later to periodically wipe from table
    sessions_table.delete(f"user_id = {user_id} AND session_id = {session_id}")
    sessions_table.add(session) 

    return response

@app.route('/extract-info', methods=['POST'])
def extract_info(user_id, query):
    prompt = f'''You are an assistant that extracts structured information from natural language queries.

Extract the following:
- interest: What general area or domain does this question relate to? (e.g., history, science, politics)
- topic: What is the main entity or subject being asked about?
- question_type: What type of question is this? (e.g., factual, opinion, comparison, definition)
- user_goal: What is the user likely trying to achieve with this query? (e.g., learning, writing a report, casual curiosity)

Query: {query}
'''
    payload = {
        "user_id": user_id,
        "prompt": prompt
    }
    return "Hello"

if __name__ == '__main__':
    app.run(port=3000, debug=True) # change port from llm_api