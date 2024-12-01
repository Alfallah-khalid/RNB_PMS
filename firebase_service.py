import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging
from functools import wraps

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class FirebaseService:
    def __init__(self):
 
        self.db = self.initialize_firebase()

    def initialize_firebase(self):
      
        if not firebase_admin._apps:
           
            with open("firebase.json", "r") as f:
                firebase_config = json.load(f)

         
            private_key = os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")
            private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")

           
            firebase_config["private_key"] = private_key
            firebase_config["private_key_id"] = private_key_id


            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)

        return firestore.client()

    
    def firestore_error_handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Firestore error in {func.__name__}: {e}")
                return False
        return wrapper



    def CU(self, path, data, document_id=None):
        try:
            # Split the path into individual parts (collections and documents)
            path_parts = path.split('/')
            
            # Initialize a reference starting from the Firestore root
            ref = self.db
            t=""
            # Loop over the path and set the correct references for collections and documents
            for i, part in enumerate(path_parts):
                if i % 2 == 0:
                    # It's a collection if the index is even (collection reference)
                    ref = ref.collection(part)
                    t="c"
                else:
                    # It's a document if the index is odd (document reference)
                    ref = ref.document(part)
                    t="d"
            
            # Add or set the final document at the specified location
            if document_id:
                # If a document ID is provided, update the document
                if t=="d":
                    ref.document(document_id).set(data, merge=True)
                    print(t)
                elif t=="c":
                    print(t)
                    ref.document(document_id).set(data, merge=True)
                return document_id
            else:
                # If no document ID, add a new document with an auto-generated ID
                print(type(ref))
                if t=="c":
                    new_doc_ref =ref.set(data)
                elif t=="d":
                    new_doc_ref =ref.set(data)
                return new_doc_ref

        except Exception as e:
            print(f"Error creating/updating document: {e}")
            return False


    @firestore_error_handler
    def G(self, collection_name, document_id):
      
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    @firestore_error_handler
    def GC(self, collection_name):
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.stream()
        return [doc.to_dict() for doc in docs if doc.exists]
    

    @firestore_error_handler
    def G2(self, path):
        try:
            # Split the path into individual parts (collections and documents)
            path_parts = path.split('/')

            # Initialize a reference starting from the Firestore root
            ref = self.db
            
            # Loop over the path and set the correct references for collections and documents
            for i, part in enumerate(path_parts):
                if i % 2 == 0:
                    # It's a collection if the index is even (collection reference)
                    ref = ref.collection(part)
                else:
                    # It's a document if the index is odd (document reference)
                    ref = ref.document(part)
            
            # Retrieve the document at the specified location
            doc = ref.get()
            return doc.to_dict() if doc.exists else None

        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None

    @firestore_error_handler
    def U(self, collection_name, document_id, data):
       
        self.db.collection(collection_name).document(document_id).update(data)
        return True

    @firestore_error_handler
    def D(self, collection_name, document_id):
      
        self.db.collection(collection_name).document(document_id).delete()
        return True

    @firestore_error_handler
    def GC(self, collection_name):
       
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.stream()
        return [doc.to_dict() for doc in docs]
