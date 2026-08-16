from pipeline.config import S3_BUCKET, S3_PREFIX
from pipeline.load.gcs_s3_blob import upload_directory_to_s3


def upload_gold_to_s3():
    """Sube los archivos Gold a Amazon S3."""

    if not S3_BUCKET:
        raise ValueError("S3_BUCKET no está configurado.")

    local_dir = "data/gold"
    prefix = f"{S3_PREFIX}/gold"

    print("\nSubiendo Gold a S3...")

    uploaded = upload_directory_to_s3(
        local_dir,
        S3_BUCKET,
        prefix,
    )

    print(f"Gold subido a S3: {uploaded} archivos")


if __name__ == "__main__":
    upload_gold_to_s3()
