import os 
import sys
import numpy as np
import pandas as pd

TARGET_COLUMN='Churn flag'
PIPELINE_NAME:str='Churn'
ARTIFACT_DIR:str='Artifacts'
FILE_NAME:str='raw_data.csv'
TRAIN_FILE_NAME:str='train.csv'
TEST_FILE_NAME:str='test.csv'
SCHEMA_FILE_PATH=os.path.join('config','schema.yaml')
COLLECTION:str='churn_data'
DATABASE:str='churn_prediction'
SAVED_MODEL_DIRECTORY=os.path.join('saved_models')



DATA_INGESTION_DIRECTORY:str='data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIRECTORY:str='feature_store'
DATA_INGESTION_INGESTED_DIRECTORY:str='ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float=0.2


DATA_VALIDATION_DIRECTORY:str='data_validation'
DATA_VALIDATION_DRIFT_REPORT_DIRECTORY:str='drift_report'
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME:str='report.yaml'
DATA_VALIDATION_VALID_DIRECTORY:str='validated'
DATA_VALIDATION_INVALID_DIRECTORY:str='invalid'