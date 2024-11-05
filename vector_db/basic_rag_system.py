from __future__ import print_function
import json
import pandas as pd
import uuid
import os
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from sentence_transformers import SentenceTransformer, util
embedder_model = SentenceTransformer("all-MiniLM-L6-v2")

class RAGVectorDB:
    def __init__(self):
        """
        Set up our database schema, with the following elements:
         - document id - a UUID just to make the record unique
         - documents - the text that gets embedded
         - embedded_vector - the embedded documents
         - metadatas - any other data you want to keep along with the record and return via search.
        """
        self.df = pd.DataFrame(columns=['ids', 'documents', 'embedded_vector', 'metadatas'])

    def embed(self, input_text):
        """
        Embed input_text using your favorite embedder
        """
        # use this with self.client = openai.OpenAI() and os.environ["OPENAI_API_KEY"] = openai_api_key if you prefer
        # response = self.client.embeddings.create(input = [input_text], model="text-embedding-3-small").data[0].embedding

        # but by default, we're gonna use the ultra-lightweight "all-MiniLM-L6-v2"
        response = embedder_model.encode(input_text)
        return response

    def add_document(self, documents, metadata):
        """
        Insert a new document with raw text and metadata. 
        This function does the rest - making UID and the embedded vector.
        """
        if documents in self.df['documents'].values:
            return None

        embedded_vector = self.embed(documents)
        doc_id = str(uuid.uuid4())

        new_row = pd.DataFrame({
            'ids': [doc_id],
            'documents': [documents],
            'embedded_vector': [embedded_vector],
            'metadatas': [json.dumps(metadata)]
        })
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        return doc_id
    
    def add_documents(self,docs:list):
        for doc in docs:
            self.add_document(doc[0],doc[1])
    
    
    def retrieve_docs_by_query(self, documents, num_neighbors=10):
        """
        Get the nearest embedded neighbor documents
        """
        query_vector = self.embed(documents)
        similarities = cosine_similarity([query_vector], self.df['embedded_vector'].tolist())[0]
        distances = euclidean_distances([query_vector], self.df['embedded_vector'].tolist())[0]
        
        # Create a dataframe with similarities
        similarity_df = pd.DataFrame({
            'index': self.df.index,
            'similarity': similarities,
            'distances': distances # OR try out: [1.0 - x for x in similarities] $ (the cosine distance)
        })
        
        # Sort by similarity in descending order and get top num_neighbors
        top_similarities = similarity_df.sort_values('similarity', ascending=False).head(num_neighbors)
        
        # Get the corresponding rows from the original dataframe
        result_df = self.df.loc[top_similarities['index']]
        
        # Add the similarity scores to the result
        result_df = result_df.reset_index(drop=True)
        result_df['similarity'] = top_similarities['similarity'].values
        result_df['distances'] = top_similarities['distances'].values
        
        return result_df
    
    def save_db(self, filename):
        # Convert embedded_vector to string for CSV storage
        df_to_save = self.df.copy()
        df_to_save['embedded_vector'] = df_to_save['embedded_vector'].apply(lambda x: ','.join(map(str, x)))
        df_to_save.to_csv(filename, index=False)

    def load_db(self, filename):
        loaded_df = pd.read_csv(filename)
        # Convert embedded_vector back to list of floats
        loaded_df['embedded_vector'] = loaded_df['embedded_vector'].apply(lambda x: [float(i) for i in x.split(',')])
        self.df = loaded_df

