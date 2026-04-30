from dataclasses import dataclass

# A dataclass is a feature in Python
# that is used to store data in a clean and structured way without writing boilerplate code
# required to create structure data containers.

@dataclass
class DataIngestionArtifact:
    train_data_file_path:str
    test_data_file_path:str

@dataclass
class DataValidationArtifact:
    validation_status:bool
    valid_train_data_file_path:str
    valid_test_data_file_path:str
    invalid_train_data_file_path:str
    invalid_test_data_file_path:str
    drift_report_file_path:str
