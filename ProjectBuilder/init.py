import configparser
import logging
import os
import subprocess
import sys

config = configparser.ConfigParser()
config.read('config.ini')


def install_package(package):
    """Install Python package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_required_packages():
    """Install required Python packages."""
    install_package('flake8')
    install_package('autopep8')


def run_flake8(directory, config_file):
    """
    Run Flake8 code quality checks on the given directory and configuration file.

    Returns the result of the Flake8 command as a CompletedProcess object.
    """
    command = ['flake8', directory]
    if config_file:
        command += ['--config', config_file]
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def auto_fix_pep8_issues(directory):
    """Automatically fix simple PEP8 issues in the given directory using autopep8."""
    subprocess.run(['autopep8', '--in-place', '--recursive', directory])


def code_review(directory, config_file):
    """Perform code review by running Flake8 code quality checks on the given directory."""
    logging.info("Running code quality checks...")
    result = run_flake8(directory, config_file)
    if result.returncode == 0:
        logging.info("No issues found.")
    else:
        logging.error("Code issues detected:\n%s", result.stdout)
        logging.info("Attempting to auto-fix simple issues...")
        auto_fix_pep8_issues(directory)
        logging.info("Re-running code quality checks...")
        result = run_flake8(directory, config_file)
        if result.returncode == 0:
            logging.info("All auto-fixable issues resolved.")
        else:
            logging.error("Some issues need manual review:\n%s", result.stdout)
            sys.exit(0)


if __name__ == "__main__":
    # Get configuration parameters
    project_dir = config['DEFAULT'].get('ProjectDirectory', '.')
    flake8_config = config['DEFAULT'].get('Flake8Config', '')

    # Check if the Flake8 configuration file exists
    if not os.path.isfile(flake8_config):
        logging.error(f"Flake8 configuration file not found at {
                      flake8_config}. Using default settings.")
        flake8_config = ''

    # Configure logging
    logging.basicConfig(filename='code_review_output.log', level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s')

    install_required_packages()
    code_review(project_dir, flake8_config)
