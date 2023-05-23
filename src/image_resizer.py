# Import necessary libraries
import boto3
import os
import sys
import json
from PIL import Image
from io import BytesIO

# Function to resize the image
def resize_image(bucket, key, size):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Create an S3 resource object
    s3_resource = boto3.resource('s3')

    # Retrieve the S3 object using the bucket and key
    obj = s3.get_object(Bucket=bucket, Key=key)

    # Open the image and convert it into a PIL Image object
    img = Image.open(BytesIO(obj['Body'].read()))

    # Resize the image
    img.thumbnail(size)

    # Create a BytesIO object
    buffer = BytesIO()

    # Save the image into the buffer in JPEG format
    img.save(buffer, 'JPEG')

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Create the key for the resized image
    resized_key = f'resized/{key}'

    # Upload the image back to S3
    s3_resource.Object(bucket, resized_key).put(Body=buffer, ContentType='image/jpeg')

# Main function
def main():
    # Create an SQS client
    sqs = boto3.client('sqs')

    # Get the SQS queue URL from environment variables
    queue_url = os.getenv('SQS_QUEUE_URL')

    # Continuously poll the SQS queue
    while True:
        # Receive a message from the SQS queue
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        # If there are any messages
        if 'Messages' in messages:
            # Get the first message and its receipt handle
            message = messages['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Parse the message body as JSON
            event = json.loads(message['Body'])

            # If there are any records in the event
            if 'Records' in event:
                # For each record, get the bucket name and key
                for record in event['Records']:
                    bucket = record['s3']['bucket']['name']
                    key = record['s3']['object']['key']

                    # Resize the image
                    resize_image(bucket, key, (200, 200))

            # Delete the message from the queue
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

# If the script is being run as the main module
if __name__ == '__main__':
    # Start the main function
    main()