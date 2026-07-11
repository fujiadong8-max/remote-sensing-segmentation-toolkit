import glob
from pathlib import Path
import numpy as np
import rasterio
from rasterio.merge import merge
from osgeo import gdal, gdalconst
import os

def rasterio_mosaic(input_dir, output_path):
    p = Path(input_dir)
    img_files0 = p.rglob("*{}".format('.tif'))
    input_files = sorted([str(path) for path in img_files0])
    # input_files = glob.glob(f"{input_dir}/*_PAN_DOM.tif")
    # print(input_files)
    # quit()
    src_files = [rasterio.open(f) for f in input_files]
    mosaic, transform = merge(src_files, method="max")  # 自动计算拼接
    
    # 保存结果（保留多通道）
    meta = src_files[0].meta.copy()
    meta.update({
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": transform,
        "compress": "lzw",
        # "BIGTIFF": "YES"
    })
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(mosaic)


if __name__ == "__main__":
    input_dir = r"D:\Data"
    output_dir = r"D:\Data\2022"
    os.makedirs(output_dir, exist_ok=True)
    output_mosaic = os.path.join(output_dir, "mosaic_max.tif")
    rasterio_mosaic(input_dir, output_mosaic)