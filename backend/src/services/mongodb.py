from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os,sys,json
from dataclasses import dataclass
from backend.src.utils.exception import customException
from backend.src.utils.logger import logging

load_dotenv()

@dataclass
class MongoDBConfig:
    uri = os.getenv("MONGO_DB_URI")
    logging.info("Mongo DB Credentials retrieved")

class MongoDB:
    def __init__(self):
        # Create a new client and connect to the server
        logging.info("Mongo DB client created")
        self.client = MongoClient(MongoDBConfig.uri, server_api=ServerApi('1'))
    
    def ping(self):
        '''
        Check if the connection is alive
        '''
        try:
            logging.info("Verifying mongo db connection")
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            logging.error(e)
            raise customException(e,sys)
    
    def insert_Data(self):
        '''
        Insert data into the database
        '''
        try:
            logging.info("Pushing data to MongoDB")
            db = self.client['Restaurant']
            db.create_collection('info')
            collection=self.client['Restaurant']['info']
            with open("F:/EatSage/backend/src/restaurantData/llmContext.txt", 'r') as file:
                data = json.load(file)
            collection.insert_many(data)
            logging.info("Pushed successfully")
        except Exception as e:
            logging.info(e)
            raise(e,sys)

if __name__=="__main__":
    mongo = MongoDB()
    mongo.insert_Data()