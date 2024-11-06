#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <username> <password> <server_address> <document_string_1> '<json_metadata>'"
    echo "Example: $0 user pass server.com 'my document' '{\"user_input_category\":\"important\",\"priority\":\"high\"}'"
    exit 1
fi

# Store command line arguments
username="$1"
password="$2"
server_name="$3"
document_string_1="$4"
metadata="$5"

# Validate that metadata is valid JSON
if ! echo "$metadata" | jq . >/dev/null 2>&1; then
    echo "Error: Provided metadata is not valid JSON"
    echo "Provided metadata: $metadata"
    exit 1
fi

# Login and get token
token_response=$(curl -s -k -X POST "https://${server_name}:5000/api/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${username}\",\"password\":\"${password}\"}")

# Extract token using jq
token=$(echo $token_response | jq -r '.token')

# Check if token extraction was successful
if [ -z "$token" ] || [ "$token" = "null" ]; then
    echo "Failed to get token. Server response:"
    echo "$token_response"
    exit 1
fi

# Construct the document payload with the provided metadata
add_response_1=$(curl -s -k -X POST "https://${server_name}:5000/api/add_document" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_doc\": [\"${document_string_1}\",${metadata}]}")

# Output the response
echo "Response from adding document 1:"
echo "$add_response_1"
