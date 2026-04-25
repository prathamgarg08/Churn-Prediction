import sys
from churn.exception.exception import ChurnException
from churn.logging.logger import logging
from churn.components.data_ingestion import DataIngestion
from churn.entity.config import DataIngestionConfig
from churn.entity.config import TrainingPipelineConfig

if __name__=="__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()

        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        data_ingestion=DataIngestion(data_ingestion_config)
        logging.info('Initiate Data Ingestion')
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
        logging.info('Data Ingestion completed')
        print(data_ingestion_artifact)
    except Exception as e:
        raise ChurnException(e,sys)