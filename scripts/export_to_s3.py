import os
from pathlib import Path

try:
    import boto3
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: boto3. Install it with `python -m pip install boto3 python-dotenv`."
    ) from exc

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DASHBOARD = ROOT / "grafana" / "dashboards" / "nexaplay-overview.json"


def read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def resolve_dashboard_path() -> Path:
    configured_path = os.getenv("DASHBOARD_FILE", str(DEFAULT_DASHBOARD)).strip()
    dashboard_path = Path(configured_path)
    if not dashboard_path.is_absolute():
        dashboard_path = ROOT / dashboard_path

    if not dashboard_path.exists():
        raise SystemExit(f"Dashboard file not found: {dashboard_path}")

    return dashboard_path


def main() -> None:
    # Design step 1:
    # Load `.env` automatically when possible so the script works the same way
    # on a local laptop and in a simple internship demo environment.
    if load_dotenv is not None:
        load_dotenv(ROOT / ".env")

    dashboard_path = resolve_dashboard_path()
    bucket_name = read_required_env("S3_BUCKET_NAME")
    region = os.getenv("AWS_DEFAULT_REGION", "eu-west-1").strip() or "eu-west-1"

    # Design step 2:
    # Keep the S3 object key predictable so repeat uploads overwrite the latest
    # dashboard snapshot instead of creating ambiguous copies.
    object_key = f"grafana-dashboards/{dashboard_path.name}"

    client = boto3.client("s3", region_name=region)
    client.upload_file(
        str(dashboard_path),
        bucket_name,
        object_key,
        ExtraArgs={"ContentType": "application/json"},
    )

    print(f"Uploaded {dashboard_path.name} to s3://{bucket_name}/{object_key}")


if __name__ == "__main__":
    main()
