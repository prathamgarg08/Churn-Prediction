import pandas as pd
import numpy as np
import re
import yaml
import pickle
import dill
import os
import sys
from churn.exception.exception import ChurnException
from churn.logging.logger import logging



def clean_industry(industry):
     try:
        if pd.isna(industry):
            return None
        industry=industry.lower()
        industry=re.sub(r"[^a-z\s]","a",industry)
        industry=industry.strip()
            
        mapping={
                "finanace":'Finance',
                'finance':'Finance',
                "retail":"Retail",
                'Heathcare':"Healthcare",
                'heathcare':"Healthcare",
                'manufacturing':"Manufacturing",
                'manufacturin':"Manufacturing",
                'TECH':"Technology",
                'technology':"Technology",
                'tech':"Technology",
                'saas':"Saas",
                'energy':"Energy"
                }
        return mapping.get(industry,industry.title()) 
     except Exception as e:
          raise ChurnException(e,sys)
    

def clean_region(region):
        try:
            if pd.isna(region):
                return None
            region=region.lower()
            region=re.sub(r"[^a-z\s]","a",region)
            region=region.strip()
            
            mapping={
                "north america":"North America",
                'n. america':"North America",
                'north americ':"North America",
                "na america":"North America",
                'latam':"Latam",
                'europe':"Europe",
                'middle east':"Middle East",
                'apac':"Apac"
                }
            return mapping.get(region,region.title())
        except Exception as e:
            raise ChurnException(e,sys)
    
def clean_sub_industry(sub_industry):
        try:
            if pd.isna(sub_industry):
                return None
            sub_industry=sub_industry.lower()
            sub_industry=re.sub(r'[^a-z\s]',"a",sub_industry)
            sub_industry=sub_industry.strip()
            
            mapping_sub_industry={
                'data':"Data",
                "ai":"AI",
                "cloud":"Cloud",
                "e-commerce":"E-commerce",
                "eacommerce":"E-commerce",
                "payments":"Payments",
                "cybersecurity":"Cybersecurity",
                'infra':"Infra"
                }
            return mapping_sub_industry.get(sub_industry,sub_industry.title())
        except Exception as e:
            raise ChurnException(e,sys)
    

def clean_contract_length_months(contract_length_months):
        try:
            if pd.isna(contract_length_months):
                return None
            mapping_month={
                "36 mnth":'36',
                "12 months":'12'
                }
            return mapping_month.get(contract_length_months,contract_length_months.title())
            
        except Exception as e:
            raise ChurnException(e,sys)
    

def clean_company_size(x):
        try:
            if pd.isna(x):
                return np.nan
            x=str(x).lower().strip()
            if 'k' in x:
                return int(float(x.replace('k',''))*1000)
            if '+' in x:
                return int(x.replace('+',''))
            return int(x)
        except Exception as e:
            raise ChurnException(e,sys)


def read_yaml_file(file_path:str)->dict:
    try:
          with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
         raise ChurnException(e,sys)

def write_yaml_file(file_path:str,content:object,replace:bool=False)->None:
     try:
          if replace:
               if os.path.exists(file_path):
                    os.remove(file_path)
          os.makedirs(os.path.dirname(file_path),exist_ok=True)
          with open(file_path,'w') as file:
               yaml.dump(content,file)
     except Exception as e:
          raise ChurnException(e,sys)
