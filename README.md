# A Simple Encrypted Local LLM Model Container, with Default Model

![An easy-to-use template](./llm_api_diagram.png?raw=true "Scematic")

This is a simple local LLM with a secure API. 
It's meant to deploy onto a VM or server, and does the following stuff:
 - HTTPS/SSL encryption using certificates (example below)
 - JWT (JSON Web Token) authentication (the user sends user credentials first and receives a token)
 - Rate limiting to prevent abuse (login/call rate limits)
 - Environment variable configuration for sensitive data
Token expiration and proper validation

Let's make a virtual environment to handle everything (use your favorite one if you prefer conda or something else):
virtualenv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Generate SSL certificates  (these are for example - in production,
 you should use proper certificates from a trusted CA):
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

Set up the .env file with proper values for the secret key and certificate paths
Run the server (preferably using gunicorn in production):

gunicorn --certfile cert.pem --keyfile key.pem -b 0.0.0.0:5000 secure-llm-api:app


# Making API Calls
To make API calls, run the script:

call_remote_llm.sh localhost 
(replace "localhost" with whatever the IP or address of the server is)

This script will first use the login credentials to get a token:
(NOTE: The -k flag allows the test/self-signed token we're making here to work,
but that should be replaced with a proper 3rd-party token in production)

curl -k -X POST https://your-server:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<username_goes_here>","password":"<password_goes_here>"}'

e.g. 

curl -k -X POST https://localhost:5000/api/login   
-H "Content-Type: application/json"   
-d '{"username":"example_username","password":"fix_this_put_in_a_real_auth_system"}'

The return will have a token:
{"token":"<your_token>"}


Then it will use this token to make a request:
curl -k -X POST https://your-server:5000/api/protected \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"input_string": "Hello, world!"}'

e.g.

curl -k -X POST https://localhost:5000/api/protected   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXhhbXBsZV91c2VybmFtZSIsImV4cCI6MTczMDYyNTk2Nn0.A2VItSPVy1t2Zk9JdTUnhoyb4gFchmSILdhykLZElRc"   -H "Content-Type: application/json"   -d '{"input_string": "Write a short poem about frogs."}'
{"response_string":"Ribbit, serenade so sweet,\nIn ponds and streams, they dance and meet,\nTheir emerald skin, a wondrous sight,\nA chorus of croaks, a joyful night.\n\nWith legs so strong, they leap with glee,\nA tiny king, they rule the sea,\nTheir beauty shines, a treasure rare,\nA simple joy, beyond compare.","user":"example_username"}


# Example Run:
Just try it out with the script like so:
./call_remote_llm.sh example_username fix_this_put_in_a_real_auth_system localhost "write a short poem about frogs."



# But Wait - I bet you came for more than just an LLM.  

So let's add a vectorDB on top.  Or two!  Give this a shot to test them out:
python vector_db/test_rag_systems.py