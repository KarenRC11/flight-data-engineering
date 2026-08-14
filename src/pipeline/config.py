import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


PROJECT_ENV = os.getenv("PROJECT_ENV", "dev")

INPUT_FILE_PATH = os.getenv(
    "INPUT_FILE_PATH",
    "./data/raw/flight_data_2024.csv",
)

OUTPUT_DIR = Path(
    os.getenv(
        "OUTPUT_DIR",
        "./data",
    )
)

CLOUD_PROVIDER = os.getenv(
    "CLOUD_PROVIDER",
    "aws",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1",
)

S3_BUCKET = os.getenv(
    "S3_BUCKET",
    "",
)

S3_PREFIX = os.getenv(
    "S3_PREFIX",
    "flight-data-engineering",
)


def show_config():
    print("PROJECT_ENV:", PROJECT_ENV)
    print("INPUT_FILE_PATH:", INPUT_FILE_PATH)
    print("OUTPUT_DIR:", OUTPUT_DIR)
    print("CLOUD_PROVIDER:", CLOUD_PROVIDER)
    print("AWS_REGION:", AWS_REGION)
    print("S3_BUCKET:", S3_BUCKET)
    print("S3_PREFIX:", S3_PREFIX)
