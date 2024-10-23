from chromadb import PersistentClient

def list_existing_collections():
    try:
        chroma_client = PersistentClient(path="chroma_stock")
        
        # Get existing collections
        existing_collections = chroma_client.list_collections()
        
        # Extract and print collection names
        collection_names = [collection.name for collection in existing_collections]
        print("Existing collections:", collection_names)
        
        return collection_names
    except Exception as e:
        print(f"Error listing collections: {e}")
        return []

# Example usage
existing_collections = list_existing_collections()