from glob import glob
import os
import numpy as np
import rasterio as rio
from tqdm import tqdm

def to_uint8(input_file, output_file, percent):
    with rio.open(input_file) as src:
        count = src.count
        meta = src.meta
        meta.update(dict(driver='GTiff', count=count, nodata=None, dtype=rio.uint8))
        out_raster = rio.open(output_file, 'w', **meta)
        for i in range(count):
            band = src.read(i + 1)
            band = band.astype(np.float32)
            mask = src.read_masks(i + 1).astype('bool')
            band[~mask] = np.nan
            low_value = np.nanpercentile(band, percent)
            high_value = np.nanpercentile(band, 100 - percent)
            tmp = np.clip(band, a_min=low_value, a_max=high_value)
            band_out = ((tmp - low_value) / (high_value - low_value)) * 255
            # band_out[band_out==np.nan] = 0
            out_raster.write(band_out.astype(np.uint8), i + 1)


if __name__ == "__main__":
    percent = 0.5
    input_path = r"C:\Users\1\Desktop\遥感地物提取\test_data_2024\images"
    output_dir = r"C:\Users\1\Desktop\遥感地物提取\test_data_2024\images_unit8"
    os.makedirs(output_dir, exist_ok=True)
    input_files = glob(input_path + '/*.tif')
    for input_file in tqdm(input_files):
        name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, name)
        to_uint8(input_file, output_file, percent)

