
from glob import glob
from pathlib import Path
from tqdm import tqdm
# from math import ceil
from raster_sample import RasterSampleDataset, window_transform
import os
import rasterio as rio


def slid_clip(src_file, dst_path, win_size, step_size, pad_size, need_tail=False, keep_tsf=False):
    src_file = Path(src_file)
    os.makedirs(dst_path, exist_ok=True)
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
    padh, padw = dataset.pad_size
    prog_bar = tqdm(total=len(dataset), desc=src_file.name)
    for img, top_x, top_y, down_x, down_y in dataset:
        winw, winh = down_x - top_x, down_y - top_y
        out = img[padh:win_size+padh, padw:win_size+padw]
        out = out[:winh, :winw]
        if keep_tsf:
            win_transform = window_transform((top_x, top_y), dataset.affine)
        else:
            win_transform = None
        
        kwds.update({
            'height': winh,
            'width': winw,
            'transform': win_transform
        })
        out_file = os.path.join(dst_path, src_file.stem + '_{}_{}.tif'.format(str(top_y), str(top_x)))
        with rio.open(out_file, 'w', **kwds) as dst:
            dst.write(out.transpose((2,0,1)))
        prog_bar.update()


def main():
    src_path = r"D:\Data\custom\test"
    dst_path = r'D:\Data\odm_s7\out3334'
    win_size = 256
    step_size = 256
    pad_size = 0
    src_files = glob(os.path.join(src_path, '*89.tif'))
    for src_file in src_files:
        slid_clip(src_file, dst_path, win_size, step_size, pad_size, need_tail=True, keep_tsf=False)

if  __name__ == '__main__':
    main()