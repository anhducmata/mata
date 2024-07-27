import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_top_k_similarities_as_string(vectors, query_final_data):
    query_vector = model.encode(query_final_data).reshape(1, -1)

    # Extract vectors and ids
    vector_list = [np.array(v.vector).reshape(1, -1) for v in vectors]
    
    # Calculate cosine similarities
    similarities = [cosine_similarity(query_vector, v)[0][0] for v in vector_list]

    # Find index of highest similarity
    top_n_indices = np.argsort(similarities)[-2:][::-1]
    
    # Return the text and similarity score of the most similar vector

    top_n_results = [{'text': vectors[idx].text, 'similarity_score': similarities[idx]} for idx in top_n_indices]
    top_n_indices_str = ', '.join(map(str, top_n_results))

    return top_n_indices_str
