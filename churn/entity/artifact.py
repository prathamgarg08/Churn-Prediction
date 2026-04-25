from dataclasses import dataclass

# A dataclass is a feature in Python
# that is used to store data in a clean and structured way without writing boilerplate code
# required to create structure data containers.

@dataclass
class DataIngestionArtifact:
    train_data_file_path:str
    test_data_file_path:str