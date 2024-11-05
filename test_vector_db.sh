#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <username> <password> <server_address> <document_string_1> <document_string_2> <document_string_3>"
    exit 1
fi

# Store command line arguments
username="$1"
password="$2"
server_name="$3"  
document_string_1="$4"
document_string_2="$5"
document_string_3="$6"

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


# Make the protected API call with the token - add some random stuff to this vector DB.
# here we're also adding random json matadata.
add_response_1=$(curl -s -k -X POST "https://${server_name}:5000/api/test_document" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_doc\": [\"${document_string_1}\",{\"user_input_category\":\"random_category_1\"}]}")

# Output the response
echo "Response from testing document 1:"
echo "$add_response_1"


# Make the protected API call with the token - add some random stuff to this vector DB.
# here we're also adding random json matadata.
add_response_1=$(curl -s -k -X POST "https://${server_name}:5000/api/add_document" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_doc\": [\"${document_string_1}\",{\"user_input_category\":\"random_category_1\"}]}")

# Output the response
echo "Response from adding document 1:"
echo "$add_response_1"


add_response_2=$(curl -s -k -X POST "https://${server_name}:5000/api/add_document" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_doc\": [\"${document_string_2}\",{\"user_input_category\":\"random_category_1\"}]}")

# Output the response
echo "Response from adding document 2:"
echo "$add_response_2"


response_3=$(curl -s -k -X POST "https://${server_name}:5000/api/query_similar_docs" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"input_string\":\"${document_string_3}\",\"num_docs\":\"5\"}")

# Output the response
echo "Response from requesting similar documents:"
echo "$response_3"