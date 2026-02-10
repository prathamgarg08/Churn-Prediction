import os
from pathlib import Path

project_name='Churn_Prediction'

list_of_files=[
    f"{project_name}/__init__.py"
    # f"{project_name}/cloud/__init__.py",
    # f"{project_name}/cloud/s3_syncer.py",
    # f"{project_name}/components/__init__.py",
    # f"{project_name}/components/data_ingestion.py",
    # f"{project_name}/components/data_transformation.py",
    # f"{project_name}/components/data_validation.py",
    # f"{project_name}/components/model_trainer.py",
    # f"{project_name}/constants/__init__.py",
    # f"{project_name}/constants/training/__init__.py",
    # f"{project_name}/entity/__init__.py",
    # f"{project_name}/entity/artifact.py",
    # f"{project_name}/entity/config.py",
    # f"{project_name}/exception/__init__.py",
    # f"{project_name}/exception/exception.py",
    # f"{project_name}/logging/__init__.py",
    # f"{project_name}/logging/logger.py",
    # f"{project_name}/pipeline/__init__.py",
    # f"{project_name}/pipeline/training_pipeline.py",
    # f"{project_name}/pipeline/prediction_pipeline.py",
    # f"{project_name}/utils/__init__.py",
    # f"{project_name}/utils/ml_utils/__init__.py",
    # f"{project_name}/utils/ml_utils/metric/__init__.py",
    # f"{project_name}/utils/ml_utils/metric/classification_metrics.py",
    # f"{project_name}/utils/ml_utils/model/__init__.py",
    # f"{project_name}/utils/ml_utils/model/estimator.py",
    # f"{project_name}/utils/main_utils/__init__.py",
    # f"{project_name}/utils/main_utils/utils.py",
    # ".gitignore",
    # "README.md",
    # ".github/workflows/main.yaml",
    # "Data/",
    # 'notebooks/EDA.ipynb',
    # "Dockerfile",
    # "app.py",
    # "main.py",
    # "setup.py",
    # ".env",
    # "push_data_mongodb.py",
]

for filepath in list_of_files:
    filepath=Path(filepath)
    filedir,filename=os.path.split(filepath)
    if filepath.suffix=="":
        os.makedirs(filepath,exist_ok=True)
        continue
    if filedir!="":
        os.makedirs(filedir,exist_ok=True)
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath)==0):
        with open(filepath,"w") as f:
            pass
    else:
        print(f"file is already created at :{filepath}")