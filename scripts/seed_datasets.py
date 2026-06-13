#!/usr/bin/env python3
"""Download Superstore CSVs from GitHub, convert to Parquet, upload to MinIO, register via API.

Usage (from repo root):
    cd backend && uv run python ../scripts/seed_datasets.py

Requires the backend to be running for the registration step.
MinIO must be running (docker-compose up minio).
"""

from __future__ import annotations

import json
import os
import urllib.request
from urllib.error import URLError

import boto3
import duckdb
from botocore.client import Config
from botocore.exceptions import ClientError

ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
KEY = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
SECRET = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
BUCKET = os.getenv("S3_BUCKET", "bi-data")
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

DATASETS = [
    (
        "sales",
        "https://raw.githubusercontent.com/chinmoy2306/superstore_sales_analysis/refs/heads/main/sales.csv",
    ),
    (
        "product",
        "https://raw.githubusercontent.com/chinmoy2306/superstore_sales_analysis/refs/heads/main/product.csv",
    ),
    (
        "customer",
        "https://raw.githubusercontent.com/chinmoy2306/superstore_sales_analysis/refs/heads/main/customer.csv",
    ),
]


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=KEY,
        aws_secret_access_key=SECRET,
        config=Config(signature_version="s3v4"),
    )


def create_bucket(s3) -> None:
    try:
        s3.create_bucket(Bucket=BUCKET)
        print(f"  Created bucket '{BUCKET}'")
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"  Bucket '{BUCKET}' already exists")
        else:
            raise


def upload_parquets() -> None:
    host = ENDPOINT.replace("https://", "").replace("http://", "")
    use_ssl = str(ENDPOINT.startswith("https")).lower()
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"SET s3_endpoint = '{host}';")
    con.execute(f"SET s3_access_key_id = '{KEY}';")
    con.execute(f"SET s3_secret_access_key = '{SECRET}';")
    con.execute(f"SET s3_use_ssl = {use_ssl};")
    con.execute("SET s3_url_style = 'path';")
    for name, url in DATASETS:
        print(f"  {name}: downloading CSV and uploading as Parquet...")
        con.execute(
            f"COPY (SELECT * FROM read_csv_auto('{url}')) "
            f"TO 's3://{BUCKET}/{name}.parquet' (FORMAT PARQUET)"
        )
        print(f"  → s3://{BUCKET}/{name}.parquet ✓")


def register_datasets() -> None:
    for name, _ in DATASETS:
        uri = f"s3://{BUCKET}/{name}.parquet"
        body = json.dumps({"name": name, "s3_uri": uri}).encode()
        req = urllib.request.Request(
            f"{API_BASE}/api/v1/datasets/register-s3",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                print(f"  Registered '{name}' → id={result['id']}")
        except URLError as exc:
            print(
                f"  Warning: could not register '{name}' (backend unreachable?): {exc}"
            )
        except Exception as exc:
            # 409 = already registered — treat as success
            if hasattr(exc, "code") and exc.code == 409:  # type: ignore[attr-defined]
                print(f"  '{name}' already registered")
            else:
                print(f"  Warning: registration failed for '{name}': {exc}")


def main() -> None:
    s3 = _s3_client()

    print("=== Step 1: Create MinIO bucket ===")
    create_bucket(s3)

    print("\n=== Step 2: Upload Parquet files ===")
    upload_parquets()

    print("\n=== Step 3: Register datasets via API ===")
    register_datasets()

    print("\nDone. Run GET /api/v1/datasets to verify.")


if __name__ == "__main__":
    main()
