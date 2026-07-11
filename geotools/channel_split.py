from glob import glob
from tqdm import tqdm
import rasterio as rio
import os

def split_channels(src_file, dst_file, channels):
    with rio.open(src_file) as src:
        profile = src.profile
        indexes = src.indexes
        profile.update(count=len(channels))
        with rio.open(dst_file, 'w', **profile) as dst:
            for k in channels:
                if k not in indexes:
                    raise ValueError(f"Channel {k} not found in source file.")
                dst.write(src.read(k), indexes=k)
if __name__ == '__main__':
    channels = [1, 2, 3]  # 假设我们只需要前三个波段
    src_path = r'D:\Data\test\test06波段提取'
    dst_path = r'D:\Data\test\test06波段提取\split'
    os.makedirs(dst_path, exist_ok=True)

    src_files = glob(src_path + '/*.tif')
    for src_file in tqdm(src_files):
        name = os.path.basename(src_file)
        dst_file = os.path.join(dst_path, name)
        split_channels(src_file, dst_file, channels)
    
    
    
    