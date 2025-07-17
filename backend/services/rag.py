from flask import jsonify
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import numpy as np
import pandas as pd
import random
import backend.setup as setup
from backend.services.embedder import embed
from backend.services.llm import ask


def collect_personal_info(query, user_id, summarized_query, tags):
    """
    Searches and retrieves the most relevant personal information entries for a given user query 
    using vector similarity and semantic tag matching.

    Parameters:
    - query (str): The original user query.
    - user_id (str): The unique identifier of the user.
    - summarized_query (str): A condensed and cleaned version of the query used for embedding.
    - tags (List[str]): A list of tags related to the query.

    Process:
    1. Embed the summarized_query.
    2. Performs vector search in the user's personal info table and selects the top_n documents (e.g top 20)
    3. Assigns a base rank score based on search result order (e.g. best result is score 20, 2nd best score 19, etc)
    4. If tags are provided:
        - Embeds the query tags and compares them with tags from personal information in the db via cosine similarity.
        - Calculates a tag match score based on semantic similarity above a threshold.
    5. Combines rank and tag scores into a final score for reranking.
    6. Returns the top K info chunks with the highest final score (only if above a threshold).
    7. Updates metadata (usage count, timestamp) for retrieved items.

    Returns:
    - A string containing the top matched personal information entries, formatted for use in prompt construction.
    """

    top_n = 20  # total results from vector search
    top_k = 5   # number to return after reranking
    sim_threshold = 0.75  # minimum cosine similarity to count as a match
    tag_weight = 1.0     # boost per matching tag

    query_embedding = embed(summarized_query if tags else query)

    try:
        # vector search (no tag filtering)
        personal_info_df = (
            setup.personal_table.search(query_embedding)
            .where(f"user_id = '{user_id}'")
            .limit(top_n)
            .to_pandas()
        )

        if not personal_info_df.empty:
            #  Rank-based similarity (top hit = top_n score)
            personal_info_df['rank_score'] = [top_n - i for i in range(len(personal_info_df))]
            # Tag similarity boost
            if not personal_info_df.empty:
                # Assign rank-based similarity score
                personal_info_df['rank_score'] = [top_n - i for i in range(len(personal_info_df))]

                if tags:
                    # Pre-embed query tags into (1, D) arrays
                    query_tag_embeddings = [np.array(embed(tag)).reshape(1, -1) for tag in tags]

                    def semantic_tag_score(row_tags):
                        if row_tags is None or len(row_tags) == 0:
                            return 0
                        try:
                            # Embed all row tags
                            row_embeddings = np.vstack([np.array(embed(t)).reshape(1, -1) for t in row_tags])
                            # Compute cosine similarity matrix: shape (len(query_tags), len(row_tags))
                            sim_matrix = cosine_similarity(np.vstack(query_tag_embeddings), row_embeddings)
                            # Count query tags with at least one row tag match above threshold
                            return (sim_matrix.max(axis=1) > sim_threshold).sum()
                        except Exception as e:
                            print(f"Tag similarity error for tags {row_tags}: {e}")
                            return 0
                    
                    # Apply semantic tag score to each row
                    personal_info_df['tag_score'] = personal_info_df['tags'].apply(semantic_tag_score)

                    # Final weighted score: rank_score + tag_score * weight
                    personal_info_df['final_score'] = personal_info_df['rank_score'] + tag_weight * personal_info_df['tag_score']
                else:
                    personal_info_df['final_score'] = personal_info_df['rank_score']


            # Rerank and select top-K
            personal_info_df = personal_info_df.sort_values(by='final_score', ascending=False)
            top_k_df = personal_info_df[personal_info_df['final_score'] >= 18].head(top_k)
            personal_info = top_k_df['info_chunk'].tolist()

            print("Info Found!")
            print(top_k_df[['info_chunk', 'rank_score', 'tag_score' if 'tag_score' in top_k_df else 'rank_score', 'final_score']])

            # update metadata, usage count and timestamp of used personal information
            for i, row in top_k_df.iterrows():
                setup.personal_table.update(where=f"info_chunk = '{row['info_chunk']}' AND user_id = '{user_id}'", values={
                    "usage_count": row['usage_count'] + 1,
                    "time_stamp": datetime.now().isoformat()
                })

        else:
            personal_info = ["(No personal info found)"]

    except Exception as e:
        print("Error in search + semantic tag reranking:", e)
        personal_info = ["(No personal info found)"]

    # Format as string for prompt use
    personal_info = '\n'.join(personal_info)

    return personal_info 

def generate_prompt(query, user_id, session_id, summarized_query, tags):
    """
    Constructs a personalized prompt for the llm by combining the user's query, 
    historical session context, and semantically matched personal information.

    Parameters:
    - query (str): The original user query.
    - user_id (str): Unique identifier for the user.
    - session_id (int): Identifier for the current session.
    - summarized_query (str): A condensed version of the query used for embedding.
    - tags (List[str]): Tags related to the current query, used for enhancing relevance of personal info retrieval.

    Returns:
    - full_prompt (str): The complete prompt to send to the language model.
    - updated_history_prompt (str): A version of the prompt history that appends the current query but excludes the generated response (for logging or future sessions).
    """
    personal_info = collect_personal_info(query, user_id, summarized_query, tags)
    print(personal_info)
    # extract prompt history
    history_prompt = (
        setup.sessions_table.search()
        .where(f"user_id = '{user_id}' AND session_id = {session_id}")
        .to_pandas()
    )
    # new session
    if history_prompt.empty: 
        full_prompt = (
            f"Additional information about the user and/or the current query {personal_info}\n"
            f"Some information may be irrelevant to the current query. " 
            f"If you deem that the case, then please ignore that piece of information\n"
            f"Query: {query}\\n"
            f"Response:"
        )
        # return the prompt, and new history prompt without the answer
        return full_prompt, f"Query: {query}\nResponse:"

    history_prompt = history_prompt['history_prompt'].tolist()
    print(history_prompt[0])
    full_prompt = (
        f"Past Queries and Responses: {history_prompt[0]}\n"
        f"Additional information about the user and/or the current query {personal_info} \n"
        f"Some information may be irrelevant to the current query. " 
        f"If you deem that the case, then please ignore that piece of information\n"
        f"Query: {query}"
        f"Response:"
    )
    # return the prompt and updated history prompt without the answer
    return full_prompt, f"{history_prompt[0]}\nQuery: {query}\nResponse:"


def generate_response(data):
    """
    Generates a response to a user query while maintaining and updating personalized session history.

    Parameters:
    - data (dict): A dictionary containing the following keys:
        - "user_id" (str): Unique identifier for the user.
        - "session_id" (int): Identifier for the current session.
        - "query" (str): The user’s natural language query.

    Returns:
    - response (str): The generated response from the language model.
    """
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    query = data.get("query")

    # extract info from user query, condense/summarize for personal info retrieval, construct prompt for querying
    summarized_query, tags = extract_info(data)
    prompt, history_prompt = generate_prompt(query, user_id, session_id, summarized_query, tags)

    # query llm
    response = ask(prompt)

    # update the history_prompt for the session to keep track of the conversation
    
    existing = setup.sessions_table.search().where(
         f"user_id = '{user_id}' AND session_id = {session_id}"
    ).to_pandas()

    if not existing.empty:
        # Session exists → update
        setup.sessions_table.update(
            where=f"user_id = '{user_id}' AND session_id = {session_id}",
            values={"history_prompt": f"{existing['history_prompt'].iloc[0]} {response}"}
        )
    else:
        # Session doesn't exist → create a new one
        setup.sessions_table.add([
            {
                "user_id": f"{user_id}",
                "session_id": session_id,
                "history_prompt": response
            }
        ])

    print(response)
    return response


def delete_session_data(data):
    # wipe the deletes in lancedb from disk
    setup.sessions_table.compact()


def clear_personal_table(data):
    """
    Cleans up the user's personal information table by removing the least relevant chunks of personal info

    Parameters:
    - data (dict): A dictionary containing the key:
        - "user_id" (str): Unique identifier for the user whose data is being cleaned.

    Find all chunks of information that are less than 1 standard deviation less than the average count value.
    Remove the REMOVE_COUNT oldest entries. If number of entries less than 1 standard deviation away from average
    is less than REMOVE_COUNT, randomly remove REMOVE_COUNT entries.

    Returns:
    - str: A message indicating how many entries were removed to maintain table size.
    """
    user_id = data.get('user_id')
    MAX_ENTRIES = 100
    REMOVE_COUNT = MAX_ENTRIES * 0.2

    current_size = len(setup.personal_table)

    if current_size < MAX_ENTRIES * 0.90:
        return "Nothing to remove"
    
    # Remove the oldest entries. Less than average count, and then sorted by timestamp
    df = (
        setup.sessions_table.search()
        .where(f"user_id = '{user_id}'")
        .to_pandas()
    )

    avg_usage = df['usage_count'].mean()
    std = df['usage_count'].std()
    print(f"Average usage count: {avg_usage:.2f}")
    print(len(df), REMOVE_COUNT)
    try: 
        # filter for chunks with count less than 1 std from average
        df_least_used = df[df['usage_count'] < (avg_usage - std)]
        df_least_used['time_stamp'] = pd.to_datetime(df['time_stamp'])
        # Sort oldest to newest
        df_least_used = df_least_used.sort_values(by='time_stamp', ascending=True)
        
        if len(df_least_used) < REMOVE_COUNT: # default to random removal if not enough entries
            raise Exception
        oldest_entries = df_least_used.head(REMOVE_COUNT)

        print("removing least relevant entries")
        for index, row in oldest_entries.iterrows(): # remove entries
            info = row['info_chunk']
            user_id = row['user_id']
            
            setup.personal_table.delete(where=f"user_id = '{user_id}' AND info_chunk = '{info}'")
    except Exception as e:
        # Randomly sample rows to drop
        print("removing randomly", min(0, int(REMOVE_COUNT)))
        print(len(df), REMOVE_COUNT)
        rows_to_drop = df.sample(n=int(REMOVE_COUNT), random_state=42)  # random_state for reproducibility
        for index, row in rows_to_drop.iterrows(): # remove entries
            info = row['info_chunk']
            user_id = row['user_id']
            
            setup.personal_table.delete(where=f"user_id = '{user_id}' AND info_chunk = '{info}'")

    return f"Removed {REMOVE_COUNT} entries from personal_table to maintain size."


def parse_extracted_info(user_id, extracted_info):
    """
    Parses and stores extracted personal information from a string into the personal information table, 
    while also returning the summarized query and tags for later use.

    Parameters:
    - user_id (str): Unique identifier for the user to whom the information belongs.
    - extracted_info (str): A string containing tab-separated info chunks and a final summarized query line.

    Parses extracted_info, for personal_information about the user, and condensed information/tags 
    regarding the user's current query.

    Returns:
    - Tuple[str, List[str]]: The summarized query and list of tags.
    - If parsing fails, returns an error message and `None`.
    """
    if not extracted_info:
        return None
    try:
        print(extracted_info)
        info_chunks = extracted_info.strip().split('\n')
        print(info_chunks)

        # last value of info_chunks is information regarding the user's current query 
        summarized_query = info_chunks[-1]
        tags = summarized_query.split('\t')[1].split(',')
        summarized_query = summarized_query.split('\t')[0]
        info_chunks = info_chunks[:-1]
        # print(extracted_info)
        for info_chunk in info_chunks: # iterate through each info_chunk extracting information and tags
            if info_chunk == '': 
                continue
            info = info_chunk.split('\t')[0] # strip for personal info e.g. "user is interested in planes"
            tags = [t.strip() for t in info_chunk.split('\t')[1].split(',')] # strip for tags ["planes", "buildings"]
            personal_info_chunk = [
                {
                    "user_id": user_id,
                    "info_chunk": info,
                    "vector": embed(info),
                    "tags": tags,
                    "usage_count": 0,
                    "time_stamp": f"{datetime.now().isoformat()}"
                }
            ]
            setup.personal_table.add(personal_info_chunk) # add personal info to db
            print(tags)
        print("Extraction complete")
    except Exception as e:
        print("Failed to extract information")
        return "Error: Failed to extract information", None
    return summarized_query, tags


def extract_info(data):
    """
    Constructs a system prompt to extract structured insights about the user and their query, 
    using both current and past interactions, and stores the results.

    Parameters:
    - data (dict): A dictionary containing the following keys:
        - "user_id" (str): Unique identifier for the user.
        - "session_id" (int): Identifier for the user's active session.
        - "query" (str): The current user query to analyze.

    Returns:
    - Tuple[str, List[str]]: The summarized query and list of tags, or `(None, None)` if nothing could be extracted.
    """
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    query = data.get('query')

    # extract the history prompt
    history_prompt = (
        setup.sessions_table.search()
        .where(f"user_id = '{user_id}' AND session_id = {session_id}")
        .to_pandas()
    )

    if history_prompt.empty:
        full_query = f"Query: {query}"
    else:
        history_prompt = history_prompt['history_prompt'].tolist()[0]
        if len(history_prompt) > 50000: # prevent going over input token limit
            history_prompt = history_prompt[len(history_prompt)-50000:]
        full_query = (
            f"Past query and answer from this conversation: {history_prompt}\n"
            f"Current query: {query}"
        )

    # prompt for extracting and formatting information from user's query
    prompt = (
        'You are an assistant that extracts structured information from natural language queries.\n'
        'Based on the current query, consider extracting the following information:\n'
        '- What general area or domain does this query relate to? (e.g., history, science, politics)\n'
        '- What is the main subject, entity, or idea in the query?\n'
        '- What type of query is this? (e.g., question, opinion, comparison, task)\n'
        '- What is the user likely trying to achieve with this query? (e.g., learning, writing a report, curiosity)\n'
        '- Anything else you can learn about the user (e.g. does the user like examples, how the user likes questions formatted)'
        'For each piece of information extracted, respond in one concise sentence '
        '(e.g. "likely is interested in planes", "may be building a RAG system", "may be interested in lancedb").\n'
        'Ensure that each piece of information can tell me something about the user.\n'
        'Respond very broadly but do not use absolutes (e.g. instead of "wants a concise response" use "may like concise responses")\n'
        'Be as concise but be specific and informative. Ensure that each sentence can stand alone without any external context. Do not use punctuation.\n'
        'More than one piece of information may be extracted from each bullet point, but do not extract more than 7 pieces of information total.\n'
        'Please consider the user\'s past queries if any. If the current query contains no new information about the user or the user\'s interest,'
        'do not extract the information. Keep in mind, you have likely been asked to extract information from the past queries, '
        'so DO NOT repeat information you think may have been extracted before. '
        'If no information can be extracted, respond with no text.\n'
        'For each piece of information list the keywords and ideas (e.g. honesty, machine learning, concise). '
        'Separate the tags from the main information using an actual tab character, not the string \\t or the letters \ and t. '
        'Return a literal tab (ASCII character 9), not an escape sequence. '
        'Separate each tag with a comma only (e.g. honesty,machine learning,concise). '
        'Please respond with each piece of information separated by one new line character.\n'
        'Finally, return one more line briefly summarizing the entire query and users interest include tags. DO NOT label the summary. Separate tags in the same way with a tab chracter\n'
        f'{full_query}'
    )
    extracted_info = ask(prompt)
    return parse_extracted_info(user_id, extracted_info)