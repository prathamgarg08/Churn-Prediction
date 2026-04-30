import sys
from churn.exception.exception import ChurnException
from churn.logging.logger import logging
from churn.components.data_ingestion import DataIngestion
from churn.components.data_validation import DataValidation
from churn.entity.config import DataIngestionConfig,DataValidationConfig
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


        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(data_ingestion_artifact,data_validation_config)
        logging.info('Initiate Data Validation')
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info('Data Validation completed')
        print(data_validation_artifact)
    except Exception as e:
        raise ChurnException(e,sys)
    
