
from s3fs import S3FileSystem, S3Map
from fsspec.mapping import FSMap
from typing import Union
from zarr import DirectoryStore
from netCDF4 import Dataset
from functools import lru_cache
import boto3
import os
from tempfile import mkdtemp
import re
def get_zarr_store(zarr_store_location, use_localstack=False,profile_name=None, **kwargs) -> Union[FSMap, DirectoryStore]:
        """
        get zarr store type
        if localstack kwargs:
        dict(use_ssl=False,
        key='ACCESS_KEY',
        secret='SECRET_KEY',
        client_kwargs=dict(
            region_name=aws_region_name,
            endpoint_url=f'http://{host}:4572'))
        otherwise:
        kwargs = dict(profile = <prof_name>, client_kwargs=dict(region_name=region))
        """
        profile_name = os.getenv('AWS_PROFILE', profile_name)
        if not use_localstack:
            kwargs = dict(profile=profile_name, client_kwargs=dict(region_name='us-west-2'))

        if zarr_store_location.startswith("s3://"):
            s3 = S3FileSystem(**kwargs)
            zarr_store = S3Map(root=zarr_store_location, s3=s3, check=False, create=True)

        else:
            zarr_store = DirectoryStore(zarr_store_location)
            zarr_store = DirectoryStore(zarr_store.dir_path())
        return zarr_store




@lru_cache(maxsize=10)
def get_dataset(input_netcdf:str, profile_name=None):
    profile_name = os.getenv('AWS_PROFILE', profile_name)
    if input_netcdf.startswith("s3://"):

        group = re.match(r's3:\/\/(.+?)\/(.+)', input_netcdf).group
        bucket_name, key = [group(ele) for ele in [1,2]]
        boto3.setup_default_session(profile_name=profile_name, region_name="us-west-2")
        s3 = boto3.resource('s3')
        temp_dir = mkdtemp()
        input_netcdf = f'{temp_dir}/{os.path.basename(key)}'

        s3.Bucket(bucket_name).download_file(key,input_netcdf )

        # fs = S3FileSystem(profile = profile_name, client_kwargs=dict(region_name="us-west-2"))
        # with fs.open(input_netcdf) as fileObj:
        #     dataset = Dataset('myname', memory=fileObj.read())
    return Dataset(input_netcdf, 'r')
