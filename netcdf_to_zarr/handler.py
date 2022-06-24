
from convert import mosaic_to_zarr
import os

def handler(event, context):
    os.chdir('/tmp')
    records = event['Records']
    for record in records:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        file_name = object_key.split('/')[-1]
        mosaic_to_zarr([f"s3://{bucket_name}/{object_key}"], f"s3://{bucket_name}/zarrs/{file_name}.zarr")

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
