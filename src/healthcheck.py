import os
import json
import boto3

from utils import upload_file
from datetime import datetime, timedelta

def main():	
	boto_session = boto3.Session()
	s3_client = boto_session.client("s3")
	s3_resource = boto3.resource("s3")

	# Initialize S3 client
	s3_client = boto_session.client("s3")
	bucket_name = ''

	sources_dir = "../sources"

	# Initialize an empty dict to store the results
	file_modification_dates = {}

	s3_file_keys = []
	# Update the s3_file_keys array by iterating through the directory
	for filename in os.listdir(sources_dir):
		if filename.startswith("sources.") and filename.endswith(".csv"):
			s3_file_keys.append(os.path.join(sources_dir, filename))

	print(s3_file_keys)
	# Iterated through the list of file keys and retrieve the last modified date
	for file_key in s3_file_keys:
		try:
			response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
			last_modified = response['LastModified']
			file_modification_dates[file_key] = last_modified
		except Exception as e:
			print(f"Error retrieving last modified date for {file_key}: {e}")

	# Check if any files are older than 3 hours
	current_time = datetime.now()
	expired = False
	for file_key, last_modified in file_modification_dates.items():
		if current_time - last_modified > timedelta(hours=3):
			expired = True
			break

	# Determine the status based on the expiration condition
	status = "expired" if expired else "success"

	# Create a dictionary to represent the result including status
	result = {"status": status, "file_modification_dates": file_modification_dates}

	# Write the result as JSON to a local file
	with open("latest-updated.json", "w") as json_file:
		json.dump(result, json_file)

	# Upload the local JSON file to S3
	upload_file("latest-updated.json", bucket_name, "latest-updated.json")


if __name__ == "__main__":
    main()