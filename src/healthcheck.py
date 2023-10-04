import os
import json

from config import get_config
from utils import upload_file, s3_client
from datetime import datetime, timedelta

def main():    
    config = get_config()
    bucket_name = config.pub_s3_bucket
    sources_dir = config.sources_dir

    # Initialize an empty dict to store the results
    file_modification_dates = {}

    s3_file_keys = []
    # Update the s3_file_keys array by iterating through the sources dir
    for filename in os.listdir(sources_dir):
        if filename.startswith("sources.") and filename.endswith(".csv"):
            s3_file_keys.append(os.path.join(sources_dir, filename))

    # Iterate through the list of file keys and retrieve the last modified date
    for file_key in s3_file_keys:
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
            last_modified = response['LastModified']
            file_modification_dates[file_key] = last_modified
        except Exception as e:
            print(f"Error retrieving last modified date for {file_key}: {e}")

    # Check if any files are older than 3 hours
    current_time = datetime.now()
    expired_count = 0
    total_files = len(file_modification_dates)

    for file_key, last_modified in file_modification_dates.items():
        if current_time - last_modified > timedelta(hours=3):
            expired_count += 1

    # Determine the status based on the expiration
    # Check if less than 80% of the files are expired
    expiry_threshold = 0.8  # 80%
    expired = (expired_count / total_files) < expiry_threshold
    status = "expired" if expired else "success"

    # Create a dict to represent the result including status
    result = {"status": status, "file_modification_dates": file_modification_dates}

    # Write the result as JSON to file
    with open("latest-updated.json", "w") as json_file:
        json.dump(result, json_file)

    # Upload the local JSON file to S3
    upload_file("latest-updated.json", config.pub_s3_bucket, "latest-updated.json")

if __name__ == "__main__":
    main()
