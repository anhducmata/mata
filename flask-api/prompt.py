def get_extraction_prompt(conversation):
    return f"""Please analyze the following conversation and provide a summary including key information for indexing. Identify the main topics, keywords, sentiment, emotions expressed, places mentioned, and people involved.
        Conversation: 
        \"\"\"
        {conversation}
        \"\"\"

        Summary:
        - Main Topics:
        - Keywords for Indexing:
        - Sentiment:
        - Emotions Expressed:
        - Places Mentioned:
        - People Involved:
        """

def get_user_question_enrich_prompt(user_question, context):
    return f"""
        Given the user's question, "{user_question}", identify and categorize the key information for effective indexing in a vector database. 
        Specifically, extract the main topics, keywords, sentiment, emotions expressed, places mentioned, and people involved. 
        Additionally, identify potential categories for organizing this information.
        Evaluate the relevance of the context to the user's question and include contextual information if it is related.

        Conversation Context: {context}
        Question: "{user_question}"
    """

def get_summrized_context_prompt(context):
    return f"""
    Given the following conversation context, provide a concise summary that captures the main points and relevant details. Include any significant topics, keywords, emotions expressed, places mentioned, and people involved.
    Conversation Context: {context}

    Summary:
    """

def generate_reponse_final_prompt(data, query_final_data, user_name='unknown'):
    return f"""
    Based on the following indexed data, generate a response that matches the tone and feeling of the original conversation. The response should reflect the same positive sentiment and excitement. If the response is meant to be from Mata or Duc, use first-person grammar.

    Indexed Data:
    {data}

    User Info: User is {user_name}.
    User Question: {query_final_data}

    Generate a concise response to the user's question based on the data:
    """
