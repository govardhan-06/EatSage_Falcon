import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.src.restaurantData.customLoader import JSONLoader
import json
from pathlib import Path
from pprint import pprint
from dataclasses import dataclass

@dataclass
class RestaurantDataConfig:
    """Configuration for the restaurant data loader."""
    file_path='./backend/src/restaurantData/restaurants.json'
    llm_context="./backend/src/restaurantData/llmContext.txt"

class RestaurantData:
    """Class for loading restaurant data from a JSON file."""
    def __init__(self):
        self.config = RestaurantDataConfig()
    
    def load_data(self):
        """Loads the restaurant data from the JSON file."""
        loader=JSONLoader(self.config.file_path)
        data=loader.load()

        with open(self.config.llm_context,'w') as f:
            for doc in data:
                f.write(doc.page_content + '\n')

if __name__=="__main__":
    r = RestaurantData()
    r.load_data()
