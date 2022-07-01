import os
import xarray as xa
import s3fs
import boto3

def create_fc_cog(grid, var, dest_path='./'):
    '''
        Creates a COG for the TRMM Full Climatology
    '''
    #grid = grid[::-1] # Orientation is flipped to the correct position
    rows = grid.to_numpy()[:, :] == 0.
    grid.to_numpy()[rows] = None

    grid.rio.set_spatial_dims(x_dim='Longitude', y_dim='Latitude', inplace=True)
    grid.rio.crs
    grid.rio.set_crs('epsg:4326')

    cog_name = f'{var}_co.tif'
    cog_path = f"{dest_path.rstrip('/')}/{cog_name}"
    grid.rio.to_raster(rf'{cog_path}', driver='COG')
    return os.path.basename(cog_path)

def create_spec_cogs(flash_rate_ds, var, dest_path='./'):
    '''
        Converts specific time data from TRMM .nc files into COGs
        TRMM Climatology Collection (Aside from the full data) contains a third coordinate
            Month, day, season, etc. which aren't actual coordinates
            Seen as raster bands by xarray, which isn't the case
            Separation of each 'band' was implemented
    '''
    grids = []
    ds_type = flash_rate_ds.dims[0]

    for grid in flash_rate_ds:
        #grid = grid[::-1] # Orientation is flipped to the correct position
        rows = grid.to_numpy()[:, :] == 0.
        grid.to_numpy()[rows] = None
        grid_index = grid.coords[ds_type].values

        grid.rio.set_spatial_dims(x_dim='Longitude', y_dim='Latitude', inplace=True)
        grid.rio.crs
        grid.rio.set_crs('epsg:4326')

        # Individual COGs are stored in a folder
        dest_folder = f"{dest_path.rstrip('/')}/{var}_cogs"
        if not os.path.isdir(dest_folder):
            os.mkdir(dest_folder)

        cog_name = f'{var}_{ds_type}_{grid_index}_co.tif'
        cog_path = f'{dest_folder}/{cog_name}'
        grid.rio.to_raster(rf'{cog_path}', driver='COG')
        grids.append(grid)

    return cog_path

def get_grid(s3uri, profile_name=None, client_kwargs=dict(region_name='us-west-2')):
    s3 = s3fs.S3FileSystem(profile=profile_name,client_kwargs=client_kwargs)
    store = s3fs.S3Map(root=s3uri, s3=s3, check=False)
    return xa.open_zarr(store=store, consolidated=True)


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

    response = s3_client.upload_file(file_name, bucket, object_name)

    return response

def handler(event, context):
    os.chdir('/tmp')
    records = event['Records']
    print(event)
    for record in records:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        file_name = object_key.split('/')[-1]
        var = f'{file_name[4:9].upper()}_LIS_FRD'
        grid = get_grid(f"s3://{bucket_name}/{object_key.replace('invoked', 'zarr')}")
        flash_rate_ds = grid[var]
        if var == 'VHRFC_LIS_FRD':
            cog_path = create_fc_cog(flash_rate_ds, var)
            # map_grid(grid)
        else:
            cog_path = create_spec_cogs(flash_rate_ds, var)

    upload_file(cog_path, bucket_name, f"cogs/{cog_path}")
    return event
