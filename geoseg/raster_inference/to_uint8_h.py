
from glob import glob
from pathlib import Path
from tqdm import tqdm
from math import ceil
from raster_sample import RasterSampleDataset
import os
import rasterio as rio
import numpy as np


def slid_clip(src_file, dst_file, win_size, step_size, pad_size, need_tail=True, keep_tsf=False):
    src_file = Path(src_file)
    dataset = RasterSampleDataset(src_file,
                                win_size=win_size,
                                step_size=step_size,
                                pad_size=pad_size,
                                need_tail=need_tail,                                
                                band_index=[1, 2, 3],  # [3,2,1]尝试修改。数据输入网络时，不管是训练还是推理都会经过数据预处理函数，所以主要保证图片读取通道顺序一致就行，mmcv默认是bgr，gdal默认是rgb
                                to_type='uint8')
    kwds = dataset.meta
    kwds.update(driver='GTiff', count=3, dtype='uint8', nodata=0, compress='lzw')
    # kwds.update(driver='GTiff', count=1, dtype='uint8', nodata=0, compress='lzw', BIGTIFF='YES')
    out_raster = rio.open(dst_file, 'w', **kwds)
    padh, padw = dataset.pad_size
    col_nums = ceil(dataset.width / win_size)
    temp_list = []
    prog_bar = tqdm(total=len(dataset), desc=src_file.name)
    for i, (img, top_x, top_y, down_x, down_y) in enumerate(dataset):
        winw, winh = down_x - top_x, down_y - top_y
        out = img[padh:win_size+padh, padw:win_size+padw]
        out = out[:winh, :winw]
            #     # if len(dataset) < 1:
        #     write_window = rio.windows.Window(xoff, yoff, winw, winh)
        #     out_raster.write(pred_label, indexes=1, window=write_window)
        # else:
        temp_list.append(out)
        if (i + 1) % col_nums == 0:
            temp_data = np.hstack(temp_list)
            write_window = rio.windows.Window(0, top_y, dataset.width, winh)
            out_raster.write(temp_data.transpose((2,0,1)), window=write_window)
            temp_list = []
        prog_bar.update()
    out_raster.close()


def main():
    src_path = r'D:\Data\test\test01'
    dst_path = r'D:\Data\test\test01\out4'
    win_size = 512
    step_size = 512
    pad_size = 0
    os.makedirs(dst_path, exist_ok=True)
    src_files = glob(src_path + '/*03.tif')
    for src_file in src_files:
        dst_file = os.path.join(dst_path, os.path.basename(src_file))
        slid_clip(src_file, dst_file, win_size, step_size, pad_size, need_tail=True, keep_tsf=True)

if  __name__ == '__main__':
    main()