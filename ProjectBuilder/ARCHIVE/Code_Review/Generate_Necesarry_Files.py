import os
from subprocess import call

# Define current working directory
cwd = os.getcwd()

# Activate Pipenv virtual environment
call(f'pipenv shell', shell=True)

# Define required packages in a list
packages = ['numpy', 'pandas', 'scipy', 'matplotlib']

# Install packages and write to requirements.txt
call(f'pipenv install {" ".join(packages)} && pip freeze > {
     cwd}/requirements.txt', shell=True)

# Exit Pipenv virtual environment
call(f'exit', shell=True)
