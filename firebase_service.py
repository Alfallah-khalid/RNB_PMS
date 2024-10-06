import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

class FirebaseService:
    def __init__(self):
        """
        Initializes the Firebase Admin SDK and Firestore client.
        Sensitive fields are loaded from environment variables, while non-sensitive
        fields are loaded from a JSON config file.
        """
        self.db = self.initialize_firebase()

    def initialize_firebase(self):
        """
        Initializes Firebase Admin SDK using the combination of environment variables and
        a service account JSON configuration.
        """
        if not firebase_admin._apps:
            # Load the service account JSON (without sensitive fields)
            with open("firebase.json", "r") as f:
                firebase_config = json.load(f)

            # Load private key from environment variable
            private_key = os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")
            private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")

            # Add the sensitive values to the config
            firebase_config["private_key"] = private_key
            firebase_config["private_key_id"] = private_key_id

            # Initialize Firebase app
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)

        # Return Firestore client
        return firestore.client()

    ### GENERIC CRUD OPERATIONS ###
    
    def CU(self, path, data, document_id=None):
        """
        Creates or updates a document in Firestore, supporting multiple levels of nested collections.
        :param path: A string representing the full path to the collection (can include multiple levels, e.g., 'collection/document/sub-collection/sub-document').
        :param data: A dictionary containing the document data.
        :param document_id: Optional. The document ID for the final level (can be None for auto-generated ID).
        :return: The document ID if successful, False otherwise.
        """
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
            
            # Add or set the final document at the specified location
            if document_id:
                # If a document ID is provided, update the document
                ref.document(document_id).set(data, merge=True)
                return document_id
            else:
                # If no document ID, add a new document with an auto-generated ID
                new_doc_ref = ref.add(data)
                return new_doc_ref[1].id

        except Exception as e:
            print(f"Error creating/updating document: {e}")
            return False



    def G(self, collection_name, document_id):
        """
        Retrieves a document from Firestore.
        :param collection_name: The name of the Firestore collection.
        :param document_id: The document ID to retrieve.
        :return: A dictionary containing the document data if found, else None.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def U(self, collection_name, document_id, data):
        """
        Updates an existing document in Firestore.
        :param collection_name: The name of the Firestore collection.
        :param document_id: The document ID to update.
        :param data: A dictionary of the data to update.
        :return: True if successful, False otherwise.
        """
        try:
            self.db.collection(collection_name).document(document_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    def D(self, collection_name, document_id):
        """
        Deletes a document from Firestore.
        :param collection_name: The name of the Firestore collection.
        :param document_id: The document ID to delete.
        :return: True if successful, False otherwise.
        """
        try:
            self.db.collection(collection_name).document(document_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def GC(self, collection_name):
        """
        Retrieves all documents in a given collection.
        :param collection_name: The name of the Firestore collection.
        :return: A list of documents (as dictionaries) if found, else empty list.
        """
        try:
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error retrieving collection: {e}")
            return []
