

from dataclasses import dataclass
from multiprocessing import Manager, Process, Queue
from multiprocessing.managers import Namespace
from os import cpu_count, environ
from os.path import splitext
from queue import Empty as QueueEmpty
from re import findall
from typing import Any, List, Set, Tuple, Union
from netCDF4 import Dataset, Group as NetCDFGroup, Variable as NetCDFVariable
from s3fs import S3FileSystem, S3Map
from zarr import (DirectoryStore, group as create_zarr_group,
                  Group as ZarrGroup, ProcessSynchronizer)
from zarr.core import Array as ZarrArray
from zarr.convenience import consolidate_metadata
import numpy as np
from mosaic_utilities import DimensionsMapping, resolve_reference_path


@dataclass
class NetcdfToZarr:
    input_netcdf_files: List[str]
    zarr_store_location: str
    aws_region_name: str

    
    
    def get_zarr_store_type(self, shared_namespace, **kwargs):
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
        if self.zarr_store_location.startswith("s3://"):
            s3 = S3FileSystem(**kwargs)
            shared_namespace.store_type = 'S3FileSystem'
            zarr_store = S3Map(root=self.zarr_store_location, s3=s3, check=False, create=True)
            shared_namespace.zarr_root = zarr_store.root
        else:
            zarr_store = DirectoryStore(self.zarr_store_location)
            shared_namespace.store_type = 'DirectoryStore'
            shared_namespace.zarr_root = zarr_store.dir_path()
            zarr_store = DirectoryStore(shared_namespace.zarr_root)
        return zarr_store


    def netcdf_to_zarr(self, **kwargs):
        """
        Convert netCDF to Zarr
        """
        process_count = min(cpu_count(), 3)
        
        with Manager() as manager:
            dim_mapping = DimensionsMapping(self.input_netcdf_files)
            
            output_queue = manager.Queue(len(self.input_netcdf_files))
            shared_namespace = manager.Namespace()
            zarr_store = self.get_zarr_store_type(shared_namespace, **kwargs)
            aggregated_dimensions = self.__copy_aggregated_dimensions(dim_mapping,
                                                         zarr_store)
            for input_granule in self.input_netcdf_files:
                output_queue.put(input_granule)
            output_workers = self.output_worker
            processes = [Process(target=output_workers,
                             args=(output_queue, zarr_store, shared_namespace,
                                   aggregated_dimensions))
                     for _ in range(process_count)]
            for output_process in processes:
                output_process.start()

    
    
    def __copy_aggregated_dimensions(self, dim_mapping: DimensionsMapping,
                                 zarr_store) -> Set[str]:
        """ Iterate through all aggregated dimensions, and their associated bounds,
        and write these dimensions to the output Zarr store. A list of
        aggregated dimensions are retained, so that the data values are not
        overwritten when writing all other variables.
        To limit this function to the scope of TRT-121, only aggregated
        temporal dimensions are considered. The aggregated spacial information
        exists in the `DimensionsMapping` instance, so the temporal check could
        be removed to allow all aggregated, 1-D grid dimensions to be inserted
        into the Zarr store.
        """
        if isinstance(zarr_store, DirectoryStore):
            zarr_root = zarr_store.dir_path()
        else:
            zarr_root = zarr_store.root

        zarr_synchronizer = ProcessSynchronizer(f'{splitext(zarr_root)[0]}.sync')
        root_group = create_zarr_group(zarr_store, overwrite=True,
                                   synchronizer=zarr_synchronizer)
        aggregated_dimensions = set()

        for output_dimension in dim_mapping.output_dimensions.values():
            if output_dimension.is_temporal():
                self.__copy_aggregated_dimension(output_dimension.dimension_path,
                                        output_dimension.values, root_group)
                aggregated_dimensions.add(output_dimension.dimension_path)

                if output_dimension.bounds_path is not None:
                    self.__copy_aggregated_dimension(output_dimension.bounds_path,
                                            output_dimension.bounds_values,
                                            root_group)
                    aggregated_dimensions.add(output_dimension.bounds_path)

        return aggregated_dimensions


    def output_worker(self, output_queue: Queue, zarr_store,shared_namespace,
                   aggregated_dimensions: Set[str]):
        """ This worker function is executed in a spawned process. It checks for
        items in the main queue, which correspond to local file paths for input
        NetCDF-4 files. If there is at least one URL left for writing, then the
        groups, variables and attributes from that NetCDF-4 file are written to
        the output Zarr store, in the related slice of the aggregated output
        array.
        """

        zarr_synchronizer = ProcessSynchronizer(
            f'{splitext(shared_namespace.zarr_root)[0]}.sync'
        )
        dim_mapping = DimensionsMapping(self.input_netcdf_files)

        while not hasattr(shared_namespace, 'exception') and not output_queue.empty():
            try:
                input_granule = output_queue.get_nowait()
            except QueueEmpty:
                break

            try:
                with Dataset(input_granule, 'r') as input_dataset:
                    input_dataset.set_auto_maskandscale(False)
                    self.__copy_group(input_dataset,
                                create_zarr_group(zarr_store, overwrite=False,
                                               synchronizer=zarr_synchronizer),
                             dim_mapping, aggregated_dimensions)
            except Exception as exception:
                # If there was an issue, save a string message from the raised
                # exception. This will cause the other processes to stop processing
                # input NetCDF-4 files.
                shared_namespace.exception = str(exception)
                raise exception

    def __copy_group(self, netcdf_group: NetCDFGroup, zarr_group: ZarrGroup,
                 dim_mapping: DimensionsMapping,
                 aggregated_dimensions: Set[str] = set()):
        """ Recursively copies the source netCDF4 group into the destination Zarr
        group, along with all sub-groups, variables, and attributes. The input
        `zarr_group` has an associated `ProcessSynchronizer` object, which
        allows for writing data to the same object from within parallel
        processes. This object is automatically propagated to child groups and
        datasets via the `require_group` and `require_dataset` class methods.
        Parameters
        ----------
        netcdf_group : netCDF4.Group
            the NetCDF group to copy from
        zarr_group : zarr.hierarchy.Group
            the existing Zarr group to copy into
        dim_mapping: mosaic_utilities.DimensionsMapping
            contains aggregated dimension values and units metadata
        aggregated_dimensions: Set[str]
            a set of full string paths of aggregated dimensions. As of TRT-121
            these are only temporal dimensions (and associated bounds variables)
        """
        self.__copy_attrs(netcdf_group, zarr_group)

        for child_group_name, child_netcdf_group in netcdf_group.groups.items():
            self.__copy_group(child_netcdf_group,
                     zarr_group.require_group(child_group_name.split('/').pop()),
                     dim_mapping, aggregated_dimensions)

        for variable_name, netcdf_variable in netcdf_group.variables.items():
            self.__copy_variable(netcdf_variable, zarr_group, variable_name,
                        dim_mapping, aggregated_dimensions)




  
    def __copy_variable(self, netcdf_variable: NetCDFVariable, zarr_group: ZarrGroup,
                    variable_name: str, dim_mapping: DimensionsMapping,
                    aggregated_dimensions: Set[str] = set()):
        """ Copies the variable from the NetCDF variable into the Zarr group,
        giving it the provided variable_name. Note, the `Group.require_dataset`
        class method instantiates a dataset that uses the `ProcessSynchronizer`
        associated with the group, so that the dataset can be safely written to
        from within multiple processes.
        Parameters
        ----------
        netcdf_variable : netCDF4.Variable
            the source variable to copy
        zarr_group : zarr.hierarchy.Group
            the group into which to copy the variable
        variable_name : string
            the variable_name of the variable in the destination group
        dim_mapping: DimensionsMapping
            an object containing aggregated dimension information.
        aggregated_dimensions: Set[str]
            a set of all dimension variable names that have been aggregated.
            This ensures that the aggregated data will not be overwritten by
            the input source data.
        """
        resolved_variable_name = resolve_reference_path(netcdf_variable,
                                                    variable_name)
        # create zarr group/dataset
        chunks = netcdf_variable.chunking()
        if chunks == 'contiguous' or chunks is None:
            chunks = netcdf_variable.shape

        if not chunks and len(netcdf_variable.dimensions) == 0:
        # Treat a 0-dimensional NetCDF variable as a zarr group
            zarr_variable = zarr_group.require_group(variable_name)
        else:
            if hasattr(netcdf_variable, 'add_offset'):
                dtype = netcdf_variable.add_offset.dtype
            elif hasattr(netcdf_variable, 'scale_factor'):
                dtype = netcdf_variable.scale_factor.dtype
            else:
                dtype = netcdf_variable.dtype

            # Derive the aggregated shape, used for both the chunk size calculation
            # and as the shape of the output Zarr variable.
            aggregated_shape = self.__get_aggregated_shape(netcdf_variable, dim_mapping,
                                                  aggregated_dimensions)
            new_chunks = self.compute_chunksize(aggregated_shape, dtype)

            fill_value = getattr(netcdf_variable, '_FillValue', 0)

            zarr_variable = zarr_group.require_dataset(variable_name,
                                                   shape=aggregated_shape,
                                                   chunks=tuple(new_chunks),
                                                   dtype=dtype,
                                                   fill_value=fill_value)

            if resolved_variable_name not in aggregated_dimensions:
                # For a non-aggregated dimension, insert input granule data
                self.__insert_data_slice(netcdf_variable, zarr_variable,
                                resolved_variable_name, dim_mapping)

        # xarray requires the _ARRAY_DIMENSIONS metadata to know how to label axes
        kwarg_attributes = {'_ARRAY_DIMENSIONS': list(netcdf_variable.dimensions)}

        # If the variable has been aggregated, the units must be used from the
        # aggregated dimension (or bounds) variable.
        if resolved_variable_name in aggregated_dimensions:
            if resolved_variable_name in dim_mapping.output_dimensions:
                aggregated_units = (
                dim_mapping.output_dimensions[resolved_variable_name].units
            )
            elif resolved_variable_name in dim_mapping.output_bounds:
                dimension_path = dim_mapping.output_bounds[resolved_variable_name]
                aggregated_units = (
                dim_mapping.output_dimensions[dimension_path].units
            )

            kwarg_attributes['units'] = aggregated_units

        self.__copy_attrs(netcdf_variable, zarr_variable, **kwarg_attributes)


    @staticmethod
    def compute_chunksize(shape: Union[tuple, list],
                      datatype: str,
                      compression_ratio: float = 1.5,
                      compressed_chunksize_byte: Union[int, str] = '10 Mi'):
        """
    Compute the chunksize for a given shape and datatype
        based on the compression requirement
    We will try to make it equal along different dimensions,
        without exceeding the given shape boundary
    Parameters
    ----------
    shape : list/tuple
        the zarr shape
    datatype: str
        the zarr data type
            which must be recognized by numpy
    compression_ratio: str
        expected compression ratio for each chunk
        default to 7.2 which is the compression ratio
            from a chunk size of (3000, 3000) with double precision
            compressed to 10 Mi
    compressed_chunksize_byte: int/string
        expected chunk size in bytes after compression
        If it's a string, assuming it follows NIST standard for binary prefix
            (https://physics.nist.gov/cuu/Units/binary.html)
            except that only Ki, Mi, and Gi are allowed.
        Space is optional between number and unit.
    Returns
    -------
    list/tuple
        the regenerated new zarr chunks
        """
        # convert compressed_chunksize_byte to integer if it's a str
        binary_prefix_conversion_map = {'Ki': 1024, 'Mi': 1048576, 'Gi': 1073741824}
        if type(compressed_chunksize_byte) == str:
            try:
                (value, unit) = findall(
                r'^\s*([\d.]+)\s*(Ki|Mi|Gi)\s*$', compressed_chunksize_byte
                )[0]
            except IndexError:
                raise ValueError('Chunksize needs to be either an integer or '
                             'string. If it\'s a string, assuming it follows '
                             'NIST standard for binary prefix '
                             '(https://physics.nist.gov/cuu/Units/binary.html)'
                             ' except that only Ki, Mi, and Gi are allowed.')

            compressed_chunksize_byte = int(float(value)) * int(binary_prefix_conversion_map[unit])

        # get product of chunksize along different dimensions before compression
        if compression_ratio < 1.:
            raise ValueError('Compression ratio < 1 found when estimating chunk size.')
        chunksize_unrolled = int(
        compressed_chunksize_byte * compression_ratio / np.dtype(datatype).itemsize
        )

        # compute the chunksize by trying to make it equal along different dimensions,
        #    without exceeding the given shape boundary
        suggested_chunksize = np.full(len(shape), 0)
        shape_array = np.array(shape)
        dim_to_process = np.full(len(shape), True)
        while not (~dim_to_process).all():
            chunksize_remaining = chunksize_unrolled // suggested_chunksize[~dim_to_process].prod()
            chunksize_oneside = int(pow(chunksize_remaining, 1 / dim_to_process.sum()))
            if (shape_array[dim_to_process] >= chunksize_oneside).all():
                suggested_chunksize[dim_to_process] = chunksize_oneside
                dim_to_process[:] = False
            else:
                dim_to_fill = dim_to_process & (shape_array < chunksize_oneside)
                suggested_chunksize[dim_to_fill] = shape_array[dim_to_fill]
                dim_to_process[dim_to_fill] = False

        # return new chunks
        suggested_chunksize = type(shape)(suggested_chunksize.tolist())
        return suggested_chunksize

    
    def __copy_attrs(self, netcdf_input: Union[NetCDFVariable, NetCDFGroup],
                 zarr_output: Union[ZarrGroup, ZarrArray], **kwargs):
        """ Copies all attributes from the source group or variable into the
        destination group or variable. If the Zarr store already has that
        attribute, it is not overwritten. For example, the units attribute of
        aggregated temporal dimensions.
         Converts netCDF4 variable values from their native type (typically
         Numpy dtypes) into JSON-serializable values that Zarr can store
        Parameters
        ----------
        netcdf_input : netCDF4.Group | netCDF4.Variable
            The source from which to copy attributes
        zarr_output : zarr.hierarchy.Group | zarr.core.Array
            The destination into which to copy attributes.
        **kwargs : dict
            Additional attributes to add to the destination
        """
        existing_attributes = set(zarr_output.attrs.keys())
        new_attributes = {key: self.__netcdf_attr_to_python(getattr(netcdf_input, key))
                      for key in netcdf_input.ncattrs()}

        new_attributes.update(kwargs)

        for existing_attribute in existing_attributes:
            new_attributes.pop(existing_attribute, None)

        zarr_output.attrs.update(new_attributes)

    @staticmethod
    def __insert_data_slice(netcdf_variable: NetCDFVariable, zarr_variable: ZarrArray,
                        variable_name: str, dim_mapping: DimensionsMapping):
        """ A helper function that identifies the index ranges in the aggregated
        output dimension into which the input values from the NetCDF-4
        variable should be inserted, and then updates the output Zarr store
        with these data.
        """
        netcdf_file_path = netcdf_variable.group().filepath()

        dimension_indices = []

        for dimension in netcdf_variable.dimensions:
            dimension_path = resolve_reference_path(netcdf_variable, dimension)

            if (
                dimension_path in dim_mapping.output_dimensions
                and dim_mapping.output_dimensions[dimension_path].is_temporal()
            ):
                output_dimension = dim_mapping.output_dimensions[dimension_path]
                input_dimension = (dim_mapping.input_dimensions[dimension_path]
                                                           [netcdf_file_path])
                input_values = input_dimension.get_values(output_dimension.units)
                output_indices = np.where(np.in1d(output_dimension.values,
                                              input_values))[0]

                # This assumes that all input grid values from a single granule
                # represent a continuous segment of the output dimension. Also,
                # `slice(m, n)` will address from element `m`, up to (but not
                # including) `n`, so need to extend the upper end of the slice by 1
                # to include all input data.
                dimension_indices.append(slice(output_indices.min(),
                                           output_indices.max() + 1))
            else:
                # Currently only supporting temporal aggregation. Other dimensions,
                # such as spatial dimensions, are assumed to be identical in all
                # input granules.
                dimension_indices.append(slice(None))

        zarr_variable[tuple(dimension_indices)] = netcdf_variable[:]


    def __netcdf_attr_to_python(self, val: Any) -> Any:
        """
    Given an attribute value read from a NetCDF file (typically a numpy type),
    returns the value as a Python primitive type, e.g. np.integer -> int.
    Returns the value unaltered if it does not need conversion or is unrecognized
    Parameters
    ----------
    val : any
        An attribute value read from a NetCDF file
    Returns
    -------
    any
        The converted value
        """
        if isinstance(val, np.integer):
            return int(val)
        elif isinstance(val, np.floating):
            return float(val)
        elif isinstance(val, np.ndarray):
            return [self.__netcdf_attr_to_python(v) for v in val.tolist()]
        elif isinstance(val, bytes):
            # Assumes bytes are UTF-8 strings.  This holds for attributes.
            return val.decode('utf-8')
        else:
            return 

if __name__ == "__main__":
    input_netcdf_files = ["/Users/amarouane/Downloads/lis_vhrfc_1998_2013_v01.nc"]
    zarr_store_location = "s3://sbxamarouane-private/zarr_folders/lis_vhrfc.zarr"
    aws_region_name = "us-west-2"
    netcdftozarr = NetcdfToZarr(input_netcdf_files, zarr_store_location, aws_region_name)
    kwargs = dict(profile = "WSBX", client_kwargs=dict(region_name="us-west-2"))
    foo = netcdftozarr.netcdf_to_zarr(**kwargs)
    print("Hello")