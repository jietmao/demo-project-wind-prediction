from pathlib import Path

import click
from boto3 import Session


def upload_file(data_file, key, bucket="project-bucket"):
    boto_session = Session(profile_name="localstack")
    s3_client = boto_session.client("s3")
    s3_client.upload_file(Filename=data_file, Bucket=bucket, Key=key)


@click.command()
@click.option("--data_file", default="wind_dataset.csv")
def main(data_file):
    filename = Path(data_file).name
    upload_file(data_file, f"input/{filename}")


if __name__ == "__main__":
    main()
