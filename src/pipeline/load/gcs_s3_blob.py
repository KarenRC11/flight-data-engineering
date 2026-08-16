from pathlib import Path

import boto3


def upload_file_to_s3(
    file_path: str | Path,
    bucket: str,
    key: str,
) -> str:
    """
    Sube un archivo local a Amazon S3.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {file_path}"
        )

    s3 = boto3.client("s3")

    s3.upload_file(
        str(file_path),
        bucket,
        key,
    )

    s3_uri = f"s3://{bucket}/{key}"

    print(f"Archivo subido a: {s3_uri}")

    return s3_uri


def upload_directory_to_s3(
    local_dir: str | Path,
    bucket: str,
    prefix: str,
) -> int:
    """
    Sube todos los archivos de un directorio a S3.

    Conserva la estructura relativa de carpetas.
    """

    local_dir = Path(local_dir)

    if not local_dir.exists():
        raise FileNotFoundError(
            f"No existe el directorio: {local_dir}"
        )

    s3 = boto3.client("s3")

    uploaded = 0

    for file_path in local_dir.rglob("*"):

        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(local_dir)

        key = f"{prefix.rstrip('/')}/{relative_path}"

        s3.upload_file(
            str(file_path),
            bucket,
            key,
        )

        print(f"Subido: s3://{bucket}/{key}")

        uploaded += 1

    print(f"\nTotal archivos subidos: {uploaded}")

    return uploaded
