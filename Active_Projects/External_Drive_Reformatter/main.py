# main.py
from review import run_code_review
from config import load_config
from report import generate_report

if __name__ == "__main__":
    config = load_config('config.ini')
    issues = run_code_review(config['directory'], config['flake8_settings'])
    generate_report(issues)
