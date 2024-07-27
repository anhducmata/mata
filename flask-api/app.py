from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sentence_transformers import SentenceTransformer

from prompt import (
    get_user_question_enrich_prompt,
    generate_reponse_final_prompt,
    get_summrized_context_prompt,
    get_extraction_prompt
)
from chatgpt_client import call
from vector_handler import get_top_k_similarities_as_string
from utils import chunk_text
import os
from flask_cors import CORS
from openai import OpenAI

# Initialize the Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
frontend_base_url = f"""{os.getenv('BASE_URL')}:3000"""
db = SQLAlchemy(app)

CORS(app)

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
api_key = os.getenv('CHATGPT_API_KEY')
client = OpenAI(
    api_key=api_key
 )

# Define the DataVector model
class DataVector(db.Model):
    __tablename__ = 'datavector'
    id = db.Column(db.Integer, primary_key=True)
    vector = db.Column(ARRAY(db.Float), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, vector, text):
        self.vector = vector
        self.text = text

# Define a route to handle POST requests for adding text data and embedding into vectors
@app.route('/train', methods=['POST'])
def insert_and_embed():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    text = request.json['text']
    summarized = call(client, get_extraction_prompt(text))
    segments = chunk_text(summarized, 5000, 40)
    segment_vectors = [model.encode(segment.strip()).tolist() for segment in segments]
    
    for segment, vector in zip(segments, segment_vectors):
        new_vector = DataVector(text=segment, vector=vector)
        db.session.add(new_vector)
    
    db.session.commit()
    return jsonify({'status': 'Success'}), 201

# Define a route to handle POST requests for querying similar vectors
@app.route('/ask', methods=['POST'])
def query_similar():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    context_prompt_response_data = call(client, get_summrized_context_prompt(session.get('default_session')))
    query_text = request.json['text']
    query_final_data = call(client, get_user_question_enrich_prompt(query_text, context_prompt_response_data))
    
    vectors = DataVector.query.all()
    top_n_indices_str = get_top_k_similarities_as_string(vectors, query_final_data)
    
    summarized = call(client, generate_reponse_final_prompt(top_n_indices_str, query_text))
    return jsonify({'results': summarized}), 200

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000)