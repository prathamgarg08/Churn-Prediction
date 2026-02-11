"""
setup.py turns your project from “just folders and scripts” into a real, 
installable Python package that works everywhere. It is a file that is an essential part of packaging and distributing python projects. 
It is used by setuptools (or distutils in older python versions) to define the configuration of your project
such as metadata,dependencies and more, -e . in requirements.txt
is referring to the setup.py file which will execute it and setup the python project as a package

"-e .":
Reads setup.py
Builds your project as a package
Adds it to site-packages
Registers all submodules
Installs dependencies

Conclusion: setup.py allows your code to be installed, 
not just run and deployment/production environments only understand installed code.
"""

from setuptools import setup,find_packages
from typing import List

def get_requirements()->List[str]:
    requirement_lst:List[str]=[]
    
    try:
        with open('requirements.txt','r') as file:
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print('requirements.txt not found')
    
    return requirement_lst

setup(
    name='Churn Prediction',
    version='0.0.1',
    author='Pratham Garg',
    description='Subscription-Based Churn Prediction System',
    packages=find_packages(),
    install_requires=get_requirements()
)
   