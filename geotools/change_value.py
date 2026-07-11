# -*- coding: utf-8 -*-

import os
import rasterio as rio
from glob import glob
from tqdm import tqdm
import numpy as np
from skimage import io
palette_list = [[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]

def change_value(infile, outfile, class_map):
    color_maps = {idx: i for idx, i in enumerate(palette_list)}
    with rio.open(infile) as src:
        kwds = src.profile
        datas = src.read(1)
    kwds.update(count=1, compress='lzw', dtype='uint8', nodata=0)
    data_out = np.zeros_like(datas).astype(np.uint8)
    out_raster = rio.open(outfile, 'w', **kwds)
    # data_out[datas==7] = 1
    for key, value in class_map.items():
        data_out[datas==key] = value
        
    out_raster.write(data_out, indexes=1)
    out_raster.write_colormap(1, color_maps)
    out_raster.close()

# def ski_change_value(infile, outfile, class_map):
#     datas = io.imread(infile)
#     data_out = np.zeros_like(datas)
#     for key, value in class_map.items():
#         data_out[datas==key] = value
#     io.imsave(outfile, data_out, check_contrast=False)


if __name__ == "__main__":
    class_map = {101:2, 104:1, 115:3} 
    src_path = r"D:\Data"
    out_path = r"D:\Data\111"
    os.makedirs(out_path, exist_ok=True)
    imgs_path = sorted(glob(src_path + '/*2025.tif'))
    for img_path in tqdm(imgs_path, ascii=True):
        name = os.path.basename(img_path)
        out_file = os.path.join(out_path, name)
        change_value(img_path, out_file, class_map)
