import boto3
import os

s3_client = boto3.client('s3')
bucket_name = 'your-bucket-name'
file_path = 'path/to/local/file.txt'
object_key = 'folder/file.txt'
s3_client.upload_file(file_path, bucket_name, object_key)