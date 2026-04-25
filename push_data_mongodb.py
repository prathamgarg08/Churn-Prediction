## ETL Pipeline (Extract data from local and load the raw data in mongodb)

import os
import sys
import json
import certifi
import pandas as pd
import numpy as np
import pymongo
from churn.exception.exception import ChurnException
from churn.logging.logger import logging
from dotenv import load_dotenv

load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)
ca=certifi.where()

class ChurnDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise ChurnException(e,sys)
    
    def csv_to_json_converter(self,file_path):
        try:
            df=pd.read_csv(file_path)
            df.reset_index(drop=True,inplace=True)
            records=list(json.loads(df.T.to_json()).values())
            return records
        except Exception as e:
            raise ChurnException(e,sys)
    
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.records=records
            self.database=database
            self.collection=collection
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            self.database=self.mongo_client[self.database]
            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)
            return(len(self.records))
        except Exception as e:
            raise ChurnException(e,sys)

if __name__=='__main__':
    FILE_PATH="Data\\raw_data.csv"
    DATABASE="churn_prediction"
    Collection="churn_data"
    churnobj=ChurnDataExtract()
    records=churnobj.csv_to_json_converter(file_path=FILE_PATH)
    print(records)
    no_of_records=churnobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)



    