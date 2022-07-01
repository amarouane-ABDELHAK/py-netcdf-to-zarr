
from convert import mosaic_to_zarr
import os
import boto3


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    with open(file_name, "a") as f:
        f.write("Now the file has more content!")


    response = s3_client.upload_file(file_name, bucket, object_name)

    return response

def handler(event, context):
    os.chdir('/tmp')
    records = event['Records']
    for record in records:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        file_name = object_key.split('/')[-1]
        mosaic_to_zarr([f"s3://{bucket_name}/{object_key}"], f"s3://{bucket_name}/zarrs/{file_name}.zarr")
        upload_file(f"/tmp/{file_name}.invoked", bucket_name, f"zarrs/{file_name}.invoked")

    return event



if __name__ == "__main__":
    event = {'Records': [{'eventVersion': '2.1',
   'eventSource': 'aws:s3',
   'awsRegion': 'us-west-2',
   's3': {'s3SchemaVersion': '1.0',
    'configurationId': 'tf-s3-lambda-2',
    'bucket': {'name': 'innovation-netcdfs',
     'ownerIdentity': {'principalId': ''},
     'arn': 'arn:aws:s3:::innovation-netcdfs'},
    'object': {'key': 'ncs/lis_vhrfc_1998_2013_v01.nc',
     'size': 12,
     'eTag': '',
     'sequencer': ''}}}]}
    handler(event, {})
