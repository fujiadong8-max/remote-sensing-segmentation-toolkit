# import os
# from glob import glob
# from tqdm import tqdm
# from math import ceil
# from itertools import product
from pathlib import Path
# from typing import Iterable
# from itertools import repeat
# from pyproj import CRS
import rasterio as rio
# import fiona
# import numpy as np

# from rasterio import features
# from affine import Affine
# from shapely import geometry
# from simplification.cutil import simplify_coords_vwp



class BaseRasterData:

    def __init__(self, fname):
        self.fname = fname
        self._band = rio.open(self.fname)

    def __del__(self):
        self._band.close()

    @property
    def indexes(self):
        return self._band.indexes
    @property
    def width(self):
        return self._band.width

    @property
    def height(self):
        return self._band.height

    @property
    def count(self):
        """Band counts."""
        return self._band.count

    @property
    def crs(self):
        return self._band.crs

    @property
    def affine(self):
        """Transform matrix as the `affine.Affine`
        
        This transform maps pixel row/column coordinates to coordinates in the dataset’s coordinate reference system.
        
        affine.identity is returned if if the file does not contain transform
        """
        return self._band.transform
        # return self._band.affine

    @property
    def nodata(self):
        """
        Band nodata value, type depends on the image dtype; None if the nodata value is not specified
        """
        return self._band.nodata

    @property
    def res(self):
        """
        分辨率
        Spatial resolution (x_res, y_res) of the Band in X and Y directions of the georeferenced coordinate system,
        derived from tranaform. Normally is equal to (transform.a, - transform.e)
        """
        return self._band.res

    @property
    def shape(self):
        """
        The raster dimension as a Tuple (height, width)
        """
        return self.height, self.width

    @property
    def name(self):
        """
        Name of the file, without extension and the directory path
        """
        return Path(self._band.name).stem

    @property
    def suffix(self):
        """
        Name of the file, without extension and the directory path
        """
        return Path(self._band.name).suffix

    @property
    def bounds(self):
        """
        边界(left, bottom, right, top)
        Georeferenced bounds - bounding box in the CRS of the image, based on transform and shape
        
        Returns:
            `BoundingBox object
            <https://rasterio.readthedocs.io/en/latest/api/rasterio.coords.html#rasterio.coords.BoundingBox>`_:
            (left, bottom, right, top)
        """
        return self._band.bounds

    @property
    def meta(self):
        """
        影像元信息
        The basic metadata of the associated rasterio DatasetReader
        """
        # return self._band.meta
        return self._band.profile

    @property
    def dtype(self):
        """
        Numerical type of the data stored in raster, according to numpy.dtype
        """
        return self._band.dtypes[0]

    # @property
    # def minmax(self):
    #     """
    #     Get the min and max value for each band.
    #     """
    #     TILE_SIZE = 512
    #     if self.height > self.width:
    #         downscale_factor = TILE_SIZE / self.height
    #     else:
    #         downscale_factor = TILE_SIZE / self.width

    #     rkwargs = dict(out_shape=(1, int(self.height * downscale_factor),
    #                               int(self.width * downscale_factor)),
    #                    resampling=rio.enums.Resampling.nearest)
    #     buf = np.stack([
    #         self._band.read(b, **rkwargs, masked=True) for b in self.band_index
    #     ])

    #     mins = buf.min(axis=(1, 2)).data
    #     maxs = buf.max(axis=(1, 2)).data

    #     return mins, maxs

