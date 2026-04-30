from datetime import datetime
import os
from churn.constants import training

class TrainingPipelineConfig:
    def __init__(self,timestamp=None):
        if timestamp is None:
            timestamp=datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

        self.timestamp:str=timestamp
        self.pipeline_name=training.PIPELINE_NAME
        self.artifact_name=training.ARTIFACT_DIR
        self.artifact_dir=os.path.join(self.artifact_name,self.timestamp)
        self.model_dir=os.path.join('final_model')

class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        
        self.data_ingestion_dir:str=os.path.join(
            training_pipeline_config.artifact_dir,training.DATA_INGESTION_DIRECTORY
        )

        self.feature_store_file_path:str=os.path.join(
            self.data_ingestion_dir,training.DATA_INGESTION_FEATURE_STORE_DIRECTORY,
            training.FILE_NAME
        )

        self.training_data_file_path:str=os.path.join(
            self.data_ingestion_dir,training.DATA_INGESTION_INGESTED_DIRECTORY,
            training.TRAIN_FILE_NAME
        )

        self.test_data_file_path:str=os.path.join(
            self.data_ingestion_dir,training.DATA_INGESTION_INGESTED_DIRECTORY,
            training.TEST_FILE_NAME
        )

        self.train_test_split_ratio:float=training.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.collection_name:str=training.COLLECTION
        self.database_name:str=training.DATABASE


class DataValidationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        
        self.data_validation_dir:str=os.path.join(
            training_pipeline_config.artifact_dir,training.DATA_VALIDATION_DIRECTORY
        )

        self.valid_data_dir:str=os.path.join(
            self.data_validation_dir,training.DATA_VALIDATION_VALID_DIRECTORY
        )

        self.invalid_data_dir:str=os.path.join(
            self.data_validation_dir,training.DATA_VALIDATION_INVALID_DIRECTORY
        )

        self.valid_train_data_file_path:str=os.path.join(
            self.valid_data_dir,training.TRAIN_FILE_NAME
        )

        self.valid_test_data_file_path:str=os.path.join(
            self.valid_data_dir,training.TEST_FILE_NAME
        )

        self.invalid_train_data_file_path:str=os.path.join(
            self.invalid_data_dir,training.TRAIN_FILE_NAME
        )

        self.invalid_test_data_file_path:str=os.path.join(
            self.invalid_data_dir,training.TEST_FILE_NAME
        )

        self.drift_report_file_path:str=os.path.join(
            self.data_validation_dir,training.DATA_VALIDATION_DRIFT_REPORT_DIRECTORY,
            training.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
        )





