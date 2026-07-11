from affine import Affine
import rasterio as rio
from glob import glob
from tqdm import tqdm
import os


def slide_merge(slid_path, save_path):
    slid_files = glob(slid_path + '/*.tif')
    x_max = max([int(os.path.splitext(slid_file)[0].split('_')[-1]) for slid_file in slid_files])
    y_max = max([int(os.path.splitext(slid_file)[0].split('_')[-2]) for slid_file in slid_files])
    tail_file = glob(slid_path + '/*{}_{}.tif'.format(y_max, x_max))[0]
    with rio.open(tail_file) as ref_src:
        kwds = ref_src.profile
        total_width = x_max + ref_src.width
        total_height = y_max + ref_src.height
        new_transform = ref_src.window_transform(((-y_max, total_height), (-x_max, total_width)))  # 计算指定像素窗口的地理变换矩阵

        kwds.update(
            width=total_width,
            height=total_height,
            transform=new_transform,
            dtype=ref_src.dtypes[0], compress='lzw'
        )
    save_file = os.path.join(save_path, os.path.basename(tail_file).replace('_{}_{}.tif'.format(y_max, x_max), '.tif'))
    with rio.open(save_file, 'w', **kwds) as dst:
        for slid_file in tqdm(slid_files):
            x0 = int(os.path.splitext(slid_file)[0].split('_')[-1])
            y0 = int(os.path.splitext(slid_file)[0].split('_')[-2])
            with rio.open(slid_file) as src:
                x1 = src.width + x0
                y1 = src.height + y0
                dst.write(src.read(), window=((y0, y1), (x0, x1)))

if __name__ == "__main__":
    slid_path = r'C:\Users\1\Desktop\遥感地物提取\Try2_addcolor'
    save_path = r'C:\Users\1\Desktop\遥感地物提取\Try2_merge'
    os.makedirs(save_path, exist_ok=True)
    slide_merge(slid_path, save_path)