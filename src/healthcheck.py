import json

from config import get_config
from utils import upload_file, s3_client
from datetime import datetime, timedelta
from sentry_sdk import capture_message

config = get_config()

def main():    
    bucket_name = config.pub_s3_bucket
    sources_files = config.sources_dir.glob("sources.*_*.csv")

    # Initialize an empty dict to store the results
    file_modification_dates = {}
	
    # Iterate through the list of file keys and retrieve the last modified date
    for file_key in sources_files:
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
            last_modified = response['LastModified']
            file_modification_dates[file_key] = last_modified
        except Exception as e:
            print(f"Error retrieving last modified date for {file_key}: {e}")

    json_content = {}
    expired_files = []
    expired_count = 0
    current_time = datetime.now()
    total_files = 0


    # Check if any files are older than 3 hours
    for file_key, last_modified in file_modification_dates.items():
      time_difference = current_time - last_modified
      is_file_expired = time_difference > timedelta(hours=3)
      json_content[file_key] = { expired: is_file_expired }
      if is_file_expired:
        expired_count += 1
        expired_files.append(file_key)

    # Determine the status based on the expiration
    # Check if less than 80% of the files are expired
    expiry_threshold = 0.8  # 80%
    expired = (expired_count / total_files) < expiry_threshold
    status = "expired" if expired else "success"

    # Create a dict to represent the result including status
    result = {"status": status, "files": json_content}

    # Write the result as JSON to file
    with open("latest-updated.json", "w") as json_file:
        json.dump(result, json_file)

    # Upload the local JSON file to S3
    upload_file("latest-updated.json", config.pub_s3_bucket)

     # Send a message to Sentry about the expired files
    if expired_files:
        capture_message(f"The following files are expired: {', '.join(expired_files)}")

if __name__ == "__main__":
    main()
