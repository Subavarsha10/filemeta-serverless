import boto3
import os
import urllib.parse
import mimetypes
import json

# AWS services
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# DynamoDB table
table = dynamodb.Table("filemetadata")


def lambda_handler(event, context):

    # Get information about the uploaded file
    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]

    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"]
    )

    print("File received:", key)

    # Get file information from S3
    response = s3.head_object(
        Bucket=bucket,
        Key=key
    )

    # Extract metadata
    file_name = os.path.basename(key)

    file_size = response["ContentLength"]

    extension = os.path.splitext(file_name)[1].lower()

    content_type = response.get(
        "ContentType",
        mimetypes.guess_type(file_name)[0]
    )

    # Categorize the file
    if extension == ".pdf":
        category = "Study Material"

    elif extension in [".doc", ".docx"]:
        category = "Assignment"

    elif extension in [".py", ".java", ".c", ".cpp"]:
        category = "Source Code"

    elif extension in [".ppt", ".pptx"]:
        category = "Presentation"

    elif extension in [".jpg", ".jpeg", ".png"]:
        category = "Image"

    else:
        category = "Other"

    # Create metadata record
    metadata = {
        "file_id": key,
        "file_name": file_name,
        "file_type": content_type,
        "extension": extension,
        "file_size": file_size,
        "category": category,
        "bucket": bucket,
        "upload_date": response["LastModified"].isoformat()
    }

    # Store metadata in DynamoDB
    table.put_item(
        Item=metadata
    )

    print("Metadata:")
    print(json.dumps(metadata, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps(
            "File metadata extracted successfully!"
        )
    }
