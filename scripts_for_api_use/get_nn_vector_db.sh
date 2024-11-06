#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <username> <password> <server_address> <document_string_1>"
    exit 1
fi

# Store command line arguments
username="$1"
password="$2"
server_name="$3"  
document_string_1="$4"


# Login and get token
token_response=$(curl -s -k -X POST "https://${server_name}:5000/api/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${username}\",\"password\":\"${password}\"}")

# Extract token using jq (make sure jq is installed)
token=$(echo $token_response | jq -r '.token')

# Check if token extraction was successful
if [ -z "$token" ] || [ "$token" = "null" ]; then
    echo "Failed to get token. Server response:"
    echo "$token_response"
    exit 1
fi


response_1=$(curl -s -k -X POST "https://${server_name}:5000/api/query_similar_docs" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_string\":\"${document_string_1}\",\"num_docs\":\"5\"}")

# Output the response
echo "Response from requesting similar documents:"
echo "$response_1"