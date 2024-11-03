from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from functools import wraps
from datetime import datetime, timezone
from config import Config
from llama_local import LocalLLM

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
@limiter.limit("5 per minute")  # Stricter limit for login attempts
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

if __name__ == '__main__':
    # Run with SSL in production
    app.run(
        ssl_context=(app.config['SSL_CERTIFICATE'], app.config['SSL_KEY']),
        host='0.0.0.0',
        port=5000
    )