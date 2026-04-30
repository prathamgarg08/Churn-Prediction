import pandas as pd
import numpy as np
import sys
import json
import os
from pandas import DataFrame
from churn.entity.artifact import DataIngestionArtifact,DataValidationArtifact
from churn.entity.config import DataValidationConfig
from churn.exception.exception import ChurnException
from churn.logging.logger import logging
from churn.utils.main_utils.utils import read_yaml_file,write_yaml_file
from churn.constants.training import SCHEMA_FILE_PATH
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self.schema_config=read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise ChurnException(e,sys)
    
    @staticmethod
    def read_data(file_path) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ChurnException(e, sys)
    

    def validate_number_of_columns(self,df:DataFrame)->bool:
        try:
            status=len(df.columns)==len(self.schema_config['columns'])
            logging.info(f"Is required column present: [{status}]")
            return status
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def validate_column_names(self,df:DataFrame)->bool:
        try:
            expected_columns=set(self.schema_config['columns'].keys())
            actual_columns=set(df.columns)

            missing=expected_columns - actual_columns
            extra= actual_columns - expected_columns

            if missing:
                logging.warning(f"Missing columns: {missing}")
            
            if extra:
                logging.warning(f"Extra/unexpected columns: {extra}")
            
            return len(missing)==0
            
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def is_columns_exist(self,df:DataFrame)->bool:
        try:
            df_columns=df.columns
            missing_numerical_columns=[]
            missing_categorical_columns=[]

            for col in self.schema_config['numerical_columns']:
                if col not in df_columns:
                    missing_numerical_columns.append(col)
            
            if len(missing_numerical_columns)>0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")

            for cat_cols in self.schema_config['categorical_columns']:
                if cat_cols not in df.columns:
                    missing_categorical_columns.append(cat_cols)
            
            if len(missing_categorical_columns)>0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")
            
            return False if len(missing_numerical_columns) > 0 or len(missing_categorical_columns) > 0 else True        
        
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def validate_data_types(self,df:DataFrame)->bool:
        try:
            expected_dtypes=self.schema_config.get('dtypes',{})
            mismatches=[]

            for col, expected_dtype in expected_dtypes.items():
                if col in df.columns:
                    if str(df[col].dtype) != expected_dtype:
                        mismatches.append(
                            f"{col}: expected {expected_dtype}, got {df[col].dtype}"
                        )
            if mismatches:
                logging.info(f"Dtype mismatches: {mismatches}")
                return False
            return True
        except Exception as e:
            raise ChurnException(e,sys)
    

    def validate_numerical_ranges(self,df:DataFrame)->bool:
        try:
            ranges=self.schema_config.get('numerical_ranges',{})
            status=True

            for column,bounds in ranges.items():
                if column not in df.columns:
                    continue
                col_min=bounds.get('min')
                col_max=bounds.get('max')

                if col_min is not None:
                    violated=df[df[column] < col_min]
                    if not violated.empty:
                        logging.warning(
                        f"Column '{column}' has {len(violated)} rows below min ({col_min}). "
                        f"Lowest value found: {df[column].min()}"
                    )
                        status=False
                
                if col_max is not None:
                    violated = df[df[column] > col_max]
                if not violated.empty:
                    logging.warning(
                        f"Column '{column}' has {len(violated)} rows above max ({col_max}). "
                        f"Highest value found: {df[column].max()}"
                    )
                    status = False
            return status
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def write_categorical_report(self,report:dict,label:dict):
        try:
            report_path=os.path.join(
                os.path.dirname(self.data_validation_config.drift_report_file_path),
                f"categorical_report_{label}.yaml"
            )
            os.makedirs(os.path.dirname(report_path),exist_ok=True)
            write_yaml_file(file_path=report_path,content=report)
            logging.info(f"Categorical Values report written to: {report_path}")
        except Exception as e:
            raise ChurnException(e,sys)
    
    
    def validate_categorical_values(self,df:DataFrame,dataset_label:str='dataset')->bool:
        try:
            allowed_values=self.schema_config.get('categorical_allowed_values',{})
            status=True
            report={}

            for col,allowed in allowed_values.items():
                if col not in df.columns:
                    logging.error(
                    f"[{dataset_label}] Categorical column '{col}' "
                    f"is defined in schema but missing from dataframe."
                )
                    report[col]={
                        "result": "FAILED — column missing from dataframe",
                        "expected_categories": allowed,
                        "found_categories": [],
                        "unexpected_values": [],
                        "unexpected_row_count": 0
                    }
                    status=False
                    continue
                
                actual_values=df[col].copy().fillna('nan').astype(str).str.strip()
                allowed_set=set(str(v).strip() for v in allowed)
                found_categories=set(actual_values.unique())

                unexpected= found_categories - allowed_set
                if not unexpected:
                    logging.info(
                    f"[{dataset_label}] '{col}' — all values within "
                    f"allowed categories. Unique values: {len(found_categories)}"
                )
                    report[col] = {
                    "result": "PASSED",
                    "expected_categories": sorted(allowed_set),
                    "found_categories": sorted(found_categories),
                    "unexpected_values": [],
                    "unexpected_row_count": 0
                }
                    
                else:
                    unexpected_mask= ~actual_values.isin(allowed_set)
                    unexpected_row_count=int(unexpected_mask.sum())
                    unexpected_ratio=round(unexpected_mask.mean(),4)

                #      # Sample up to 5 unexpected rows for diagnostics
                #     sample_rows = (
                #     df[unexpected_mask][[col]]
                #     .head(5)
                #     .to_dict(orient="records")
                # )
                    
                #     logging.error(
                #     f"[{dataset_label}] '{col}' has {len(unexpected)} "
                #     f"unexpected category value(s): {unexpected}. "
                #     f"Affects {unexpected_row_count} rows ({unexpected_ratio:.2%})."
                # )
                #     report[col] = {
                #     "result": "FAILED — unexpected categories found",
                #     "expected_categories": sorted(allowed_set),
                #     "found_categories": sorted(found_categories),
                #     "unexpected_values": sorted(unexpected),
                #     "unexpected_row_count": unexpected_row_count,
                #     "unexpected_row_ratio": unexpected_ratio,
                #     "sample_unexpected_rows": sample_rows
                # }
                # status = False

                never_seen = allowed_set - found_categories
                never_seen_meaningful = never_seen - {"nan"}
                
                if never_seen_meaningful:
                    logging.warning(
                    f"[{dataset_label}] '{col}' — these allowed categories "
                    f"were never seen in data: {never_seen_meaningful}. "
                    f"Could indicate upstream data loss."
                )
                report[col]["never_seen_categories"] = sorted(never_seen_meaningful)

            self.write_categorical_report(report, dataset_label)

            failed = [col for col, info in report.items() if "FAILED" in info["result"]]
            passed = [col for col, info in report.items() if info["result"] == "PASSED"]
            
            logging.info(f"[{dataset_label}] Categorical validation summary:")
            logging.info(f" Total categorical columns checked : {len(report)}")
            logging.info(f" Passed : {len(passed)}")
            logging.info(f" Failed : {len(failed)} → {failed}")

            return status

        except Exception as e:
            raise ChurnException(e,sys)
    
    def detect_data_drift(self,reference_df:DataFrame,current_df:DataFrame)->bool:
        try:
            data_drift_profile=Profile(sections=[DataDriftProfileSection()])

            data_drift_profile.calculate(reference_df,current_df)

            report=data_drift_profile.json()
            json_report=json.loads(report)

            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path,
                            content=json_report)
            
            n_features=json_report['data_drift']['data']['metrics']['n_features']
            n_drifted_features=json_report['data_drift']['data']['metrics']['n_drifted_features']

            logging.info(f"{n_drifted_features}/{n_features} drift detected.")
            drift_status=json_report['data_drift']['data']['metrics']['dataset_drift']
            return drift_status
        except Exception as e:
            raise ChurnException(e,sys)
    

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            error_messages = []
            
            # ── Step 1: Read data ──────────────────────────────────────────────
            logging.info("Reading train and test data from ingestion artifact.")
            train_df = DataValidation.read_data(
            self.data_ingestion_artifact.train_data_file_path
            )
            
            test_df = DataValidation.read_data(
            self.data_ingestion_artifact.test_data_file_path
            )
            logging.info(f"Train shape: {train_df.shape} | Test shape: {test_df.shape}")

        # ── Step 2: Column count check ─────────────────────────────────────
        # Must run first — if column count is wrong, name/dtype checks are
        # meaningless and may throw confusing errors
            logging.info("Step 2: Validating number of columns.")
            if not self.validate_number_of_columns(train_df):
                error_messages.append(
                f"Train data: column count mismatch. "
                f"Expected {len(self.schema_config['columns'])}, "
                f"got {len(train_df.columns)}."
                )
            
            if not self.validate_number_of_columns(test_df):
                error_messages.append(
                f"Test data: column count mismatch. "
                f"Expected {len(self.schema_config['columns'])}, "
                f"got {len(test_df.columns)}."
                )

        # ── Step 3: Column name check ──────────────────────────────────────
        # Run before dtype/existence checks — wrong names cause false failures
        # downstream
            logging.info("Step 3: Validating column names.")
            
            if not self.validate_column_names(train_df):
                error_messages.append(
                "Train data: column name mismatch with schema."
                )
            if not self.validate_column_names(test_df):
                error_messages.append(
                "Test data: column name mismatch with schema."
                )

        # ── Step 4: Numerical and categorical column existence check ───────
        # Confirms expected columns are present by type before dtype checks
            logging.info("Step 4: Checking numerical and categorical column existence.")
            if not self.is_columns_exist(train_df):
                error_messages.append(
                "Train data: one or more required numerical/categorical "
                "columns are missing."
                )
            if not self.is_columns_exist(test_df):
                error_messages.append(
                "Test data: one or more required numerical/categorical "
                "columns are missing."
                )

        # ── Step 5: Halt early if structure is broken ──────────────────────
        # No point running value-level checks if columns are missing/wrong
        # All downstream checks assume correct structure
            if error_messages:
                raise Exception(
                f"Structural validation failed — halting before value checks.\n"
                + "\n".join(f"  [{i+1}] {msg}" for i, msg in enumerate(error_messages))
                )

        # ── Step 6: Data type validation ───────────────────────────────────
        # Must run before categorical/range checks — wrong dtypes cause
        # incorrect comparisons in those checks
            logging.info("Step 6: Validating column data types.")
            if not self.validate_data_types(train_df):
                error_messages.append("Train data: dtype mismatch with schema.")
            
            if not self.validate_data_types(test_df):
                error_messages.append("Test data: dtype mismatch with schema.")

        # ── Step 7: Numerical range validation ────────────────────────────
        # Catches negative values in product_hours_3m, product_hours_12m etc.
            logging.info("Step 7: Validating numerical ranges.")
            
            if not self.validate_numerical_ranges(train_df):
                error_messages.append(
                "Train data: numerical range violations found."
                )
            
            if not self.validate_numerical_ranges(test_df):
                error_messages.append(
                "Test data: numerical range violations found."
                )

        # ── Step 8: Categorical value validation ──────────────────────────
        # Check Industry, Region etc. against allowed values in schema
        # Runs after dtype check — needs correct object dtype to compare
            logging.info("Step 8: Validating categorical values.")
            
            if not self.validate_categorical_values(train_df, dataset_label="train"):
                error_messages.append(
                "Train data: unexpected categorical values found."
                )
            
            if not self.validate_categorical_values(test_df, dataset_label="test"):
                error_messages.append(
                "Test data: unexpected categorical values found."
                )

        # ── Step 9: Data drift detection ─────────────────────────────────
        # Runs last — needs clean, validated data from both sides to be meaningful
        # Drift is a WARNING not a hard failure — pipeline continues
            logging.info("Step 9: Detecting data drift between train data and test data.")
            drift_status = self.detect_data_drift(
            reference_df=train_df,
            current_df=test_df
            )
            if drift_status:
                logging.warning(
                "Dataset drift detected — review drift_report.yaml. "
                "Pipeline will continue but model performance may be affected."
                )
            else:
                logging.info("No significant dataset drift detected.")

        # ── Step 10: Final hard failure check ─────────────────────────────
            if error_messages:
                raise Exception(
                f"Data Validation failed with {len(error_messages)} error(s):\n"
                + "\n".join(f"  [{i+1}] {msg}" for i, msg in enumerate(error_messages))
                )

        # ── Step 11: Save validated data ──────────────────────────────────
            logging.info("Step 11: All checks passed — saving validated data.")
            os.makedirs(
            os.path.dirname(self.data_validation_config.valid_train_data_file_path),
            exist_ok=True
            )
            train_df.to_csv(
            self.data_validation_config.valid_train_data_file_path,
            index=False, header=True
            )
            test_df.to_csv(
            self.data_validation_config.valid_test_data_file_path,
            index=False, header=True
            )
            logging.info(
            f"Validated train saved to: "
            f"{self.data_validation_config.valid_train_data_file_path}"
            )
            logging.info(
            f"Validated test saved to: "
            f"{self.data_validation_config.valid_test_data_file_path}"
            )

        # ── Step 12: Return artifact ───────────────────────────────────────
            data_validation_artifact = DataValidationArtifact(
            validation_status=True,
            valid_train_data_file_path=self.data_validation_config.valid_train_data_file_path,
            valid_test_data_file_path=self.data_validation_config.valid_test_data_file_path,
            invalid_train_data_file_path=None,
            invalid_test_data_file_path=None,
            drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            logging.info(f"Data validation artifact created: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise ChurnException(e, sys)