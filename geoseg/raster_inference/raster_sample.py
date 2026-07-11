# import os
# from glob import glob
# from tqdm import tqdm
# from math import ceil
# from itertools import product
# from pathlib import Path
# from typing import Iterable
# from itertools import repeat
# from pyproj import CRS
import rasterio as rio
# import fiona
import numpy as np
# from pathlib import Path
# from rasterio import features
from affine import Affine
# from shapely import geometry
# from simplification.cutil import simplify_coords_vwp
from .raster_base import BaseRasterData

def window_transform(window, transform):
    """Construct an affine transform matrix relative to a window.
    
    Args:
        window (Window): The input window.
        transform (Affine): an affine transform matrix.
    Returns:
        (Affine): The affine transform matrix for the given window
    """
    # x, y = transform * (window.col_off, window.row_off)
    x, y = transform * window
    return Affine.translation(x - transform.c, y - transform.f) * transform

class RasterSampleDataset(BaseRasterData):
    """Dataset wrapper for remote sensing data.

    Args:
        fname:
        win_size:
        step_size:
        pad_size:
        band_index:
    """

    def __init__(self,
                 fname,
                 win_size=512,
                 step_size=512,
                 pad_size=0,
                 need_tail=False,
                 band_index=None,
                 to_type=None,
                 data_format='channel_last',
                 fill_nodata=0,
                 transform=None):
        super().__init__(fname=fname)

        assert data_format in (
            'channel_first',
            'channel_last'), "data format must be 'channel_first' or "
        f"'channel_last', but got type {data_format}"
        self.data_format = data_format
        self.win_size = (win_size, win_size)
        self.pad_size = (pad_size, pad_size)
        self.step_size = (step_size, step_size)
        self.need_tail = need_tail

        total_band_index = [i + 1 for i in range(self.count)]
        if band_index is None:
            self.band_index = total_band_index
        else:
            assert set(band_index).issubset(set(total_band_index))
            self.band_index = band_index

        self.to_type = to_type
        self.window_ids = self.get_windows_info()
        self.fill_nodata = fill_nodata
        self.transform = transform

        self.start = 0
        self.end = len(self)

    @property
    def minmax(self):
        """
        获取各波段极值
        """
        TILE_SIZE = 512
        if self.height > self.width:
            downscale_factor = TILE_SIZE / self.height
        else:
            downscale_factor = TILE_SIZE / self.width

        rkwargs = dict(out_shape=(1, int(self.height * downscale_factor),
                                  int(self.width * downscale_factor)),
                       resampling=rio.enums.Resampling.nearest)
        buf = np.stack([
            self._band.read(b, **rkwargs, masked=True) for b in self.band_index
        ])

        mins = buf.min(axis=(1, 2)).data
        maxs = buf.max(axis=(1, 2)).data

        return mins, maxs
    def bytescale(self, band, mask, cmin, cmax, dtype=np.uint8):
        '''
        位深转换
        '''
        band = np.asarray(band, dtype=float)
        dtype_in = band.dtype
        dtype_out = np.dtype(dtype)
        mask = np.asarray(mask).astype(np.bool_)

        if dtype_in == dtype_out:
            return band
        imin_out = np.iinfo(dtype_out).min
        imax_out = np.iinfo(dtype_out).max

        cmin = np.asarray(cmin)
        cmax = np.asarray(cmax)

        imin_out = cmin / cmax * imax_out
        band = (band - cmin) / (cmax - cmin) * (imax_out - imin_out) + imin_out
        band = (band.clip(imin_out, imax_out) * mask).astype(dtype_out)

        return band     
    def get_windows_info(self):
        width, height = self.width, self.height
        x_step_size, y_step_size = self.step_size
        x_size, y_size = self.win_size
        # x_list = []
        # for top_x in range(0, width, x_size):
        #     down_x = top_x + x_size if top_x + x_size <= width else width
        #     x_list.append([top_x, down_x])

        # y_list = []
        # for top_y in range(0, height, y_size):
        #     down_y = top_y + y_size if top_y + y_size <= height else height
        #     y_list.append([top_y, down_y])

        x_list = []
        for top_x in range(0, width, x_step_size):
            if top_x + x_size <= width:
                down_x = top_x + x_size 
                x_list.append([top_x, down_x])
            else:
                if self.need_tail:
                    x_list.append([top_x, width])
                    break
                else:
                    break
        y_list = []
        for top_y in range(0, height, y_step_size):
            if top_y + y_size <= height:
                down_y = top_y + y_size 
                y_list.append([top_y, down_y])
            else:
                if self.need_tail:
                    y_list.append([top_y, height])
                    break
                else:
                    break
        top_down_xy = [[i[0], j[0], i[1], j[1]] for j in y_list
                       for i in x_list]
        return top_down_xy

    def sample(self, top_x, top_y, down_x, down_y):
        """Get the values of dataset at certain positions.
        """
        xsize, ysize = self.win_size
        xpad, ypad = self.pad_size

        xmin = top_x - xpad if top_x - xpad >= 0 else 0
        ymin = top_y - ypad if top_y - ypad >= 0 else 0
        xmax = down_x + xpad if down_x + xpad <= self.width else self.width
        ymax = down_y + ypad if down_y + ypad <= self.height else self.height

        xblock, yblock = xmax - xmin, ymax - ymin
        left, top, right, bottom = 0, 0, 0, 0

        left = xpad - top_x if top_x - xpad < 0 else 0
        top = ypad - top_y if top_y - ypad < 0 else 0

        if down_x - top_x < xsize:
            right = xsize - (down_x - top_x) + xpad
        else:
            if down_x + xpad > self.width:
                right = down_x + xpad - self.width

        if down_y - top_y < ysize:
            bottom = ysize - (down_y - top_y) + ypad
        else:
            if down_y + ypad > self.height:
                bottom = down_y + ypad - self.height

        # col_off, row_off, width, height
        window = rio.windows.Window(xmin, ymin, xblock, yblock)

        bands = [
            self._band.read(k, window=window, masked=True)
            for k in self.band_index
        ]
        if self.to_type and np.dtype(self.to_type) != np.dtype(self.dtype):
            bmin, bmax = self.minmax
            msks = [
                self._band.read_masks(k, window=window)
                for k in self.band_index
            ]
            bands = [
                self.bytescale(b, msk, bmin[i], bmax[i], dtype=self.to_type)
                for i, (b, msk) in enumerate(zip(bands, msks))
            ]

        tile_image = np.stack(bands, axis=-1)
        img = np.pad(tile_image, ((top, bottom), (left, right), (0, 0)),
                     mode='reflect')

        if self.data_format == 'channel_first':
            img = img.transpose(2, 0, 1)

        return img

    def __getitem__(self, idx):
        top_x, top_y, down_x, down_y = self.window_ids[idx]
        img = self.sample(top_x, top_y, down_x, down_y)
        if self.transform is not None:
            img = self.transform(img)

        return img, top_x, top_y, down_x, down_y

    def __len__(self):
        return len(self.window_ids)

    @property
    def step(self):
        return self.step_size

    @property
    def pad(self):
        return self.pad_size


