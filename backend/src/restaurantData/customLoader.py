import json
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

class JSONLoader(BaseLoader):
    '''
    Custom Data Loader to load documents from a JSON file.
    '''
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        # Read the JSON file
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        
        # Process the JSON data into Documents
        documents = []
        for item in data:
            content = json.dumps(item)  # Convert the item to a JSON string
            documents.append(Document(page_content=content))
        
        return documents
