import os
import sys
import pandas as pd
import numpy as np
import pymongo
import certifi
import re
from churn.exception.exception import ChurnException
from churn.logging.logger import logging
from churn.entity.config import DataIngestionConfig
from churn.entity.artifact import DataIngestionArtifact
from churn.utils.main_utils.utils import (clean_industry,clean_sub_industry,clean_region,
                                          clean_company_size,clean_contract_length_months)
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise ChurnException(e,sys)
    
    def export_collection_as_dataframe(self):
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]

            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df=df.drop(columns=['_id'],axis=1)
            df.replace({'na':np.nan},inplace=True)

            return df
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def clean_dataframe(self,df:pd.DataFrame)->pd.DataFrame:
        try:
            if "industry" in df.columns:
                df['industry']=df['industry'].apply(clean_industry)
            if "region" in df.columns:
                df["region"] = df["region"].apply(clean_region)

            if "sub_industry" in df.columns:
                df["sub_industry"] = df["sub_industry"].apply(clean_sub_industry)

            if "contract_length_months" in df.columns:
                df["contract_length_months"] = df["contract_length_months"].apply(clean_contract_length_months)

            if "company_size" in df.columns:
                df["company_size"] = df["company_size"].apply(clean_company_size)
            
            df.columns=df.columns.str.replace('_','',regex=False)
            
            column_mapping = {
                "industry": "Industry",
                "subindustry": "Sub Industry",
                "region": "Region",
                "companysize": "Company size",
                "annualrevenueusd":'Annual revenue(USD)',
                "contractvalueusd":'Contract value(USD)',
                "contractlengthmonths":"Contract length(m)",
                "tenuremonths":"Tenure(m)",
                "productusagehours3m":"Product usage hours(3m)",
                "productusagehours12m":"Product usage hours(12m)",
                "loginfrequency30d":"Login frequency(30d)",
                'activeusers':"Active users",
                'licensedusers':"Licensed users",
                "analystcalls6m":"Analyst calls(6m)",
                "supporttickets6m":"Support tickets(6m)",
                "supportescalations6m":"Support escalations(6m)",
                "avgresolutiontimehrs":"Avg resolution time(hrs)",
                "npsscore":"Nps score",
                "surveyresponsecount12m":"Survey response count(12m)",
                "discountpercent":"Discount",
                "accountnotes":"Account notes",
                "churnflag":"Churn flag"}

            df = df.rename(columns=column_mapping)
            
            return df
        except Exception as e:
            raise ChurnException(e,sys)

    
    def transform_features(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df['Tenure(d)']=round(df['Tenure(m)']*30,0)
            df=df.drop(columns=['Tenure(m)'],axis=1)
            
            df['Discount']=df['Discount'].str.replace('%','',regex=True).astype(float)
            df['Discount']=df['Discount']/100

            cols_round_off=[
                 'Annual revenue(USD)',
                 'Contract value(USD)',
                 'Product usage hours(3m)', 
                 'Product usage hours(12m)',
                 'Login frequency(30d)',
                 'Avg resolution time(hrs)']
            
            for col in cols_round_off:
                df[col]=pd.to_numeric(df[col],errors='coerce')
            
            df[cols_round_off]=df[cols_round_off].round(2)
            
            df['Contract length(m)']=df['Contract length(m)'].astype("Int64")
            df['Active users']=df['Active users'].astype('Int64')
            df['Licensed users']=df['Licensed users'].astype("Int64")
            df['Analyst calls(6m)']=df['Analyst calls(6m)'].astype("Int64")
            df['Support escalations(6m)']=df['Support escalations(6m)'].astype("Int64")
            df['Support tickets(6m)']=df['Support tickets(6m)'].astype("Int64")
            df['Nps score']=df['Nps score'].astype("Int64")
            df['Survey response count(12m)']=df['Survey response count(12m)'].astype("Int64")
            df['Tenure(d)']=df['Tenure(d)'].astype("Int64")
            df['Company size']=df['Company size'].astype("Int64")
            df['Churn flag']=df['Churn flag'].astype('object')

            df['Product usage hours(3m)']=df['Product usage hours(3m)'].where(df['Product usage hours(3m)']>=0,np.nan)
            df['Product usage hours(12m)']=df['Product usage hours(12m)'].where(df['Product usage hours(12m)']>=0,np.nan)

            return df
        except Exception as e:
            raise ChurnException(e,sys)
    
    def export_data_into_feature_store(self,df:pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            df.to_csv(feature_store_file_path,index=False,header=True)
            return df
        except Exception as e:
            raise ChurnException(e,sys)
    
    def split_data_into_train_test(self,df:pd.DataFrame):
        try:
            X = df.drop(columns=['Churn flag'], axis=1)
            y = df['Churn flag']
            X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.data_ingestion_config.train_test_split_ratio,
            random_state=42,
            stratify=y 
            )

            train_set=pd.concat([X_train,y_train],axis=1)
            test_set=pd.concat([X_test,y_test],axis=1)

            logging.info("Performed train test split on the dataframe")

            logging.info("Exited split_data_as_train_test method of Data Ingestion class")

            dir_path=os.path.dirname(self.data_ingestion_config.training_data_file_path)
            os.makedirs(dir_path,exist_ok=True)
            
            logging.info(f"Exporting train and test file path")

            train_set.to_csv(self.data_ingestion_config.training_data_file_path,index=False,header=True)
            
            test_set.to_csv(self.data_ingestion_config.test_data_file_path,index=False,header=True)

            logging.info(f"Train-test split with stratification completed")

        except Exception as e:
            raise ChurnException(e,sys)
    
    def initiate_data_ingestion(self):
        try:
            df=self.export_collection_as_dataframe()
            df=self.clean_dataframe(df)
            df=self.transform_features(df)
            df=self.export_data_into_feature_store(df)
            self.split_data_into_train_test(df)
            data_ingestion_artifact=DataIngestionArtifact(
                 train_data_file_path=self.data_ingestion_config.training_data_file_path,
                 test_data_file_path=self.data_ingestion_config.test_data_file_path
            )
            return data_ingestion_artifact
        except Exception as e:
            raise ChurnException(e,sys)