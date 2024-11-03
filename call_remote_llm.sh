#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <username> <password> <server_address> <input_string>"
    exit 1
fi

# Store command line arguments
username="$1"
password="$2"
server_name="$3"  
input_string="$4"

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

# Make the protected API call with the token
protected_response=$(curl -s -k -X POST "https://${server_name}:5000/api/protected" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_string\": \"${input_string}\"}")

# Output the response
echo "Response from protected endpoint:"
echo "$protected_response"