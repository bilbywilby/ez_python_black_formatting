# code_review_script.py
import subprocess
import sys
import os
import configparser
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename=f'code_review_{datetime.now().strftime("%Y%m%d%H%M%S")}.log',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

# Function to install packages using pip


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Install Flake8 and autopep8 if they're not already installed
install('flake8')
install('autopep8')

# Function to run Flake8 and return the results


def run_flake8(directory, config_file):
    """Run flake8 on the given directory with the specified configuration."""
    command = ['flake8', directory, '--config', config_file]
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    return result

# Function to automatically fix simple issues using autopep8


def auto_fix(directory):
    """Automatically fix simple PEP8 issues in the given directory."""
    subprocess.run(['autopep8', '--in-place', '--recursive', directory])

# Function to perform code review


def code_review(directory, config_file):
    logging.info("Running code quality checks...")
    result = run_flake8(directory, config_file)
    if result.returncode == 0:
        logging.info("No issues found.")
    else:
        logging.error("Code issues detected:\n%s", result.stdout)
        logging.info("Attempting to auto-fix simple issues...")
        auto_fix(directory)
        logging.info("Re-running code quality checks...")
        result = run_flake8(directory, config_file)
        if result.returncode == 0:
            logging.info("All auto-fixable issues resolved.")
        else:
            logging.error("Some issues need manual review:\n%s", result.stdout)
            # Exit with a non-zero status to fail the CI/CD pipeline if issues are found
            sys.exit(1)


if __name__ == "__main__":
    project_dir = config['DEFAULT'].get('ProjectDirectory', '.')
    flake8_config = config['DEFAULT'].get('Flake8Config', '')

    # Check if the Flake8 configuration file exists
    if not os.path.isfile(flake8_config):
        logging.error(f"Flake8 configuration file not found at {
                      flake8_config}. Using default settings.")
        flake8_config = ''

    code_review(project_dir, flake8_config)
