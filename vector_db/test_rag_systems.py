from basic_rag_system import RAGVectorDB
import os

from local_chroma_db import LocalChromaDB
import uuid

# display options
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


#let's make some test documents to try out.
docs = [
    ["This is a document about bananas",{"topic":"fruit"}],
    ["This is a document about oranges",{"topic":"fruit"}],
    ["This is a document about apples", {"topic": "fruit"}],
    ["This is a document about strawberries", {"topic": "fruit"}],
    ["This is a document about pineapples", {"topic": "fruit"}],
    ["This is a document about grapes", {"topic": "fruit"}],
    ["This is a document about watermelons", {"topic": "fruit"}],
    ["This is a document about lemons", {"topic": "fruit"}],
    ["This is a document about blueberries", {"topic": "fruit"}],
    ["This is a document about peaches", {"topic": "fruit"}],
    ["This is a document about cherries", {"topic": "fruit"}],
    ["This is a document about kiwis", {"topic": "fruit"}],
    ["This is a document about screwdrivers", {"topic": "tools"}],
    ["This is a document about hammers", {"topic": "tools"}],
    ["This is a document about wrenches", {"topic": "tools"}],
    ["This is a document about pliers", {"topic": "tools"}],
    ["This is a document about saws", {"topic": "tools"}],
    ["This is a document about drills", {"topic": "tools"}],
    ["This is a document about tape measures", {"topic": "tools"}],
    ["This is a document about levels", {"topic": "tools"}],
    ["This is a document about chisels", {"topic": "tools"}],
    ["This is a document about screw extractors", {"topic": "tools"}],
    ["This is a document about utility knives", {"topic": "tools"}]
    ]


# Make a basic RAG Vector-DB, fill if with the documents, and save it
vec_db = RAGVectorDB()
vec_db.add_documents(docs)    
vec_db.save_db('./test_basic_db.csv')

# (Just for test) let's load it back up to be sure it works
vec_db2 = RAGVectorDB()
vec_db2.load_db('./test_basic_db.csv')

# Now get some nearest-neighbors with the RAG system
basic_rag_nn = vec_db2.retrieve_docs_by_query("I am curious about several tools, including saws and hammers",10)
print(f"\nResponse from Basic-RAG-DB NN:\n{basic_rag_nn}")



# Now let's try this with ChromaDB
c_vec_db = LocalChromaDB()

# only do this if you want to erase the DB first
c_vec_db.clear_erase_db()

c_vec_db.add_documents(docs)
chroma_rag_nn = c_vec_db.retrieve_docs_by_query("saws and hammers",10)
print(f"\nResponse from ChromaDB RAG NN:\n{chroma_rag_nn}")

# and here's what happens if we restrict to just "topic"="tools" in the DB and still want NN:
chroma_rag_nn_limited = c_vec_db.retrieve_docs_by_metadata_and_query("saws and hammers","topic", ["tools"],10)
print(f"\nResponse from ChromaDB RAG NN, Limited to topic=tools:\n{chroma_rag_nn_limited}")


