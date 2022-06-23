
from s3fs import S3FileSystem, S3Map
from fsspec.mapping import FSMap
from typing import Union
from zarr import DirectoryStore
from netCDF4 import Dataset

def get_zarr_store(shared_namespace,zarr_store_location, **kwargs) -> Union[FSMap, DirectoryStore]:
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
        if zarr_store_location.startswith("s3://"):
            s3 = S3FileSystem(**kwargs)
            shared_namespace.store_type = 'S3FileSystem'
            zarr_store = S3Map(root=zarr_store_location, s3=s3, check=False, create=True)
            shared_namespace.zarr_root = zarr_store.root
        else:
            zarr_store = DirectoryStore(zarr_store_location)
            shared_namespace.store_type = 'DirectoryStore'
            shared_namespace.zarr_root = zarr_store.dir_path()
            zarr_store = DirectoryStore(shared_namespace.zarr_root)
        return zarr_store


def get_dataset(input_netcdf:str, profile_name="default"):
    if input_netcdf.startswith("s3://"):
        fs = S3FileSystem(profile = profile_name, client_kwargs=dict(region_name="us-west-2"))
        with fs.open(input_netcdf) as fileObj:
            dataset = Dataset('myname', memory=fileObj.read())
    else:
        dataset = Dataset(input_netcdf, 'r')
    return dataset