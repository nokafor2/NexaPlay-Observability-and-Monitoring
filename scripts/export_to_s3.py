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
# Default to the starter dashboard if no custom path is provided.
DEFAULT_DASHBOARD = ROOT / "grafana" / "dashboards" / "nexaplay-overview.json"


def read_required_env(name: str) -> str:
    # Read an environment variable and trim accidental spaces.
    value = os.getenv(name, "").strip()
    if not value:
        # Stop early with a clear message if required config is missing.
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def resolve_dashboard_path() -> Path:
    # Allow the dashboard path to be overridden from `.env`.
    configured_path = os.getenv("DASHBOARD_FILE", str(DEFAULT_DASHBOARD)).strip()
    dashboard_path = Path(configured_path)
    if not dashboard_path.is_absolute():
        # Convert relative paths into absolute paths from the repository root.
        dashboard_path = ROOT / dashboard_path

    if not dashboard_path.exists():
        # Fail clearly if the JSON file has not been exported yet.
        raise SystemExit(f"Dashboard file not found: {dashboard_path}")

    return dashboard_path


def main() -> None:
    # Design step 1:
    # Load `.env` automatically when possible so the script works the same way
    # on a local laptop and in a simple internship demo environment.
    if load_dotenv is not None:
        # Load local environment variables from `.env` if python-dotenv is installed.
        load_dotenv(ROOT / ".env")

    # Find the dashboard file that will be uploaded.
    dashboard_path = resolve_dashboard_path()
    # Read the destination S3 bucket name from the environment.
    bucket_name = read_required_env("S3_BUCKET_NAME")
    # Default to `eu-west-1` if no region is supplied.
    region = os.getenv("AWS_DEFAULT_REGION", "eu-west-1").strip() or "eu-west-1"

    # Design step 2:
    # Keep the S3 object key predictable so repeat uploads overwrite the latest
    # dashboard snapshot instead of creating ambiguous copies.
    # Store the file inside a logical `grafana-dashboards/` prefix in the bucket.
    object_key = f"grafana-dashboards/{dashboard_path.name}"

    # Create an S3 client using the configured AWS credentials and region.
    client = boto3.client("s3", region_name=region)
    # Upload the dashboard JSON with the correct content type metadata.
    client.upload_file(
        str(dashboard_path),
        bucket_name,
        object_key,
        ExtraArgs={"ContentType": "application/json"},
    )

    # Print a confirmation message after a successful upload.
    print(f"Uploaded {dashboard_path.name} to s3://{bucket_name}/{object_key}")


if __name__ == "__main__":
    # Run the export flow only when the script is executed directly.
    main()
