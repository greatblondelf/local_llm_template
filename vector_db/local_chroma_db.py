from __future__ import print_function
import chromadb
import uuid
import pandas as pd

class LocalChromaDB:
    def __init__(self,collection_name="test_local_db"):
        """
        Set up a local vector DB using ChromaDB. If there already is a DB here
        then we'll jsut connect to it.
        """
        self.chroma_client = chromadb.PersistentClient(path="./local_db") #`allow_reset` to `True` in your Settings()
        print('Opening or Creating ChromaDB Collection name: ' + str(collection_name))
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        self.collection_name=collection_name
        
    def clear_erase_db(self):
        """
        Blows away the entire DB - USE WITH CAUTION!
        """
        # CAREFUL - no going back from this, we'd have to rebuild it
        self.chroma_client.delete_collection(self.collection_name)
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        print('NOTICE:  WE HAVE JUST DELETED AND RESET THE DATABASE.  REBUILD IT NEXT.')
        
    def add_documents(self,docs):
        """
        Set up our database schema, with the following elements:
         - document id - a UUID just to make the record unique
         - raw_text - the text that gets embedded
         - embedded_vector - the embedded raw_text
         - json_metadata - any other data you want to keep along with the record and return via search.
        """
        # we just insert a new document with raw text and metadata. 
        # This function does the rest - making UID and the embedded vector.
        # here the input "docs" are structured like [string_to_embed, metadata(the json record of this document, takes whatever)]
        ids = [str(uuid.uuid4()) for d in docs]
        documents = [d[0] for d in docs]
        metadata = [d[1] for d in docs]
        # "flatten" all the elements in each metadata element to strings so they "fit" in the ChromaDB metadata system
        # note that this is the biggest argument against ChromaDB - otherwise it does everything you'd want easily.
        metadata = [{key: str(val) for key, val in dict.items()} for dict in metadata]    
            
        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadata,
        )
        print('There are now ' + str(self.collection.count()) + ' Records in the Local DB')
        
    def retrieve_docs(self, query_text, num_results=10):
        """
        Get the nearest embedded neighbor documents
        """
        results = self.collection.query(
            query_texts=[query_text], # Chroma will embed this
            n_results=num_results # how many results to return
        )
        return results

    def to_df(self, results):
        returned_var = {}
        for key in results:
            try:
                print(results[key])
                returned_var.update({key:results[key][0]})
            except:
                pass
        return pd.DataFrame.from_dict(returned_var)
    
    def retrieve_docs_by_metadata_and_query(self, query_text: str,match_value: str, value_list: list,num_results: int = 10):
        
        search_val_set_clause = [{match_value: {"$eq":val}} for val in value_list]
        if value_list is None or len(value_list) < 1:
            # nothing to use for filters
            return self.retrieve_docs(query_text, num_results=num_results)
        elif len(value_list) > 1:
            # list of filters - add an "or" clause between them
            search_where_clause = {'$or': search_val_set_clause}
        else:
            # just one filter - use it directly
            search_where_clause = {match_value: value_list[0]}
            print(search_where_clause)
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=num_results,
            where=search_where_clause, # {"metadata_field": "is_equal_to_this"},
            # include=['embeddings', 'documents', 'metadatas']
        )
        return self.to_df(results)
        # pd.DataFrame.from_dict(data, orient='index')
        #return results
    
    
    def retrieve_docs_by_query(self,query_text,num_results = 10):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=num_results,
            # include=['embeddings', 'documents', 'metadatas']
        )
        return self.to_df(results)