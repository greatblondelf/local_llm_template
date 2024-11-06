from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from functools import wraps
from datetime import datetime, timezone
from config import Config
from llama_local import LocalLLM

# A useful VectorDB
from vector_db.local_chroma_db import LocalChromaDB
import pandas as pd
vec_db = LocalChromaDB()

# to use the .env file for user creds - this should be fixed to
# use a real auth system.
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Set up an LLM to use
llm = LocalLLM()

# Rate limiting to prevent DDOS/abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per minute"]
)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing token'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
@limiter.limit("50 per minute")  # Stricter limit for login attempts
def login():
    # In production, validate against your user database
    if request.json.get('username') == os.getenv('USERNAME1') and request.json.get('password') == os.getenv('PASSWORD'):
        token = jwt.encode(
            {
                'user': request.json.get('username'),
                'exp': datetime.now(timezone.utc) + app.config['JWT_ACCESS_TOKEN_EXPIRES']
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/protected', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")  # Add rate limiting specific to this endpoint
def protected():
    # Validate input
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    input_string = request.json.get('input_string')
    if not input_string:
        return jsonify({'error': 'input_string is required'}), 400
    
    if not isinstance(input_string, str):
        return jsonify({'error': 'input_string must be a string'}), 400
    
    # Optional: Add input length limit to prevent abuse
    if len(input_string) > 2000:  # Adjust limit as needed
        return jsonify({'error': 'input_string too long'}), 400

    try:
        # Process the input string
        response_string = llm.output(input_string)
        
        # Return the response
        return jsonify({
            'response_string': response_string,
            'user': request.user['user']
        })
    except Exception as e:
        # Log the error in production
        return jsonify({'error': 'Internal server error'}), 500


# Vector Database Functions:
# we add to the vector DB like the following:
# vec_db.add_document(["This is a document about utility knives", {"topic": "tools"}])    
# then we request them using lines like these:
# chroma_rag_nn = vec_db.retrieve_docs_by_query("saws and hammers",10)
# or
# TODO: Implement this one here
# chroma_rag_nn_limited = vec_db.retrieve_docs_by_metadata_and_query("saws and hammers","topic", ["tools"],10)

@app.route('/api/test_document', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")  # Add rate limiting specific to this endpoint
def test_document():
    # Validate input
    return jsonify({})


@app.route('/api/add_document', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")  # Add rate limiting specific to this endpoint
def add_document():
    # Validate input
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    input_doc = request.json.get('input_doc')
    if not input_doc:
        return jsonify({'error': 'input_doc is required'}), 400
    
    if not isinstance(input_doc, list):
        return jsonify({'error': 'input_doc must be a list with 2 elements'}), 400
    
    # Optional: Add input length limit to prevent abuse
    if len(str(input_doc)) > 2000:  # Adjust limit as needed
        return jsonify({'error': 'input document too long'}), 400

    try:
        # Process the input string
        vec_db.add_document(input_doc) 
        
        # Return the response
        return jsonify({
            'response_string': 'document added to vector database',
            'user': request.user['user']
        })
    except Exception as e:
        # Log the error in production
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/query_similar_docs', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")  # Add rate limiting specific to this endpoint
def query_similar_docs():
    # Validate input
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    input_string = request.json.get('input_string')
    if not input_string:
        return jsonify({'error': 'input_string is required'}), 400
    
    if not isinstance(input_string, str):
        return jsonify({'error': 'input_string must be a string'}), 400
    
    # Optional: Add input length limit to prevent abuse
    if len(input_string) > 2000:  # Adjust limit as needed
        return jsonify({'error': 'input_string too long'}), 400

    num_docs = request.json.get('num_docs',10)

    try:
        # Process the input string
        response = vec_db.retrieve_docs_by_query(input_string,int(num_docs))
        #response_string = llm.output(input_string)
        
        # Return the response
        return jsonify({
            'docs': str(response),
            'user': request.user['user']
        })
    except Exception as e:
        # Log the error in production
        return jsonify({'error': 'Internal server error'}), 500



if __name__ == '__main__':
    # Run with SSL in production
    app.run(
        ssl_context=(app.config['SSL_CERTIFICATE'], app.config['SSL_KEY']),
        host='0.0.0.0',
        port=5000
    )