# -*- coding: utf-8 -*-

import os
from glob import glob
import numpy as np
import rasterio as rio
from PIL import Image
from skimage import io
from tqdm import tqdm

palette_list1 = [
    [0, 192, 64], [0, 192, 64], [0, 64, 96], [128, 192, 192],
    [0, 64, 64], [0, 192, 224], [0, 192, 192], [128, 192, 64],
    [0, 192, 96], [128, 192, 64], [128, 32, 192], [0, 0, 224],
    [0, 0, 64], [0, 160, 192], [128, 0, 96], [128, 0, 192],
    [0, 32, 192], [128, 128, 224], [0, 0, 192], [128, 160, 192],
    [128, 128, 0], [128, 0, 32], [128, 32, 0], [128, 0, 128],
    [64, 128, 32], [0, 160, 0], [0, 0, 0], [192, 128, 160],
    [0, 32, 0], [0, 128, 128], [64, 128, 160], [128, 160, 0],
    [0, 128, 0], [192, 128, 32], [128, 96, 128], [0, 0, 128],
    [64, 0, 32], [0, 224, 128], [128, 0, 0], [192, 0, 160],
    [0, 96, 128], [128, 128, 128], [64, 0, 160], [128, 224, 128],
    [128, 128, 64], [192, 0, 32], [128, 96, 0], [128, 0, 192],
    [0, 128, 32], [64, 224, 0], [0, 0, 64], [128, 128, 160],
    [64, 96, 0], [0, 128, 192], [0, 128, 160], [192, 224, 0],
    [0, 128, 64], [128, 128, 32], [192, 32, 128], [0, 64, 192],
    [0, 0, 32], [64, 160, 128], [128, 64, 64], [128, 0, 160],
    [64, 32, 128], [128, 192, 192], [0, 0, 160], [192, 160, 128],
    [128, 192, 0], [128, 0, 96], [192, 32, 0], [128, 64, 128],
    [64, 128, 96], [64, 160, 0], [0, 64, 0], [192, 128, 224],
    [64, 32, 0], [0, 192, 128], [64, 128, 224], [192, 160, 0],
    [0, 192, 0], [192, 128, 96], [192, 96, 128], [0, 64, 128],
    [64, 0, 96], [64, 224, 128], [128, 64, 0], [192, 0, 224],
    [64, 96, 128], [128, 192, 128], [64, 0, 224], [192, 224, 128],
    [128, 192, 64], [192, 0, 96], [192, 96, 0], [128, 64, 192],
    [0, 128, 96], [0, 224, 0], [64, 64, 64], [128, 128, 224],
    [0, 96, 0], [64, 192, 192], [0, 128, 224], [128, 224, 0],
    [64, 192, 64], [128, 128, 96], [128, 32, 128], [64, 0, 192],
    [0, 64, 96], [0, 160, 128], [192, 0, 64], [128, 64, 224],
    [0, 32, 128], [192, 128, 192], [0, 64, 224], [128, 160, 128],
    [192, 128, 0], [128, 64, 32], [128, 32, 64], [192, 0, 128],
    [64, 192, 32], [0, 160, 64], [64, 0, 0], [192, 192, 160],
    [0, 32, 64], [64, 128, 128], [64, 192, 160], [128, 160, 64],
    [64, 128, 0], [192, 192, 32], [128, 96, 192], [64, 0, 128],
    [64, 64, 32], [0, 224, 192], [192, 0, 0], [192, 64, 160],
    [0, 96, 192], [192, 128, 128], [64, 64, 160], [128, 224, 192],
    [192, 128, 64], [192, 64, 32], [128, 96, 64], [192, 0, 192],
    [0, 192, 32], [64, 224, 64], [64, 0, 64], [128, 192, 160],
    [64, 96, 64], [64, 128, 192], [0, 192, 160], [192, 224, 64],
    [64, 128, 64], [128, 192, 32], [192, 32, 192], [64, 64, 192],
    [0, 64, 32], [64, 160, 192], [192, 64, 64], [128, 64, 160],
    [64, 32, 192], [192, 192, 192], [0, 64, 160], [192, 160, 192],
    [192, 192, 0], [128, 64, 96], [192, 32, 64], [192, 64, 128],
    [64, 192, 96], [64, 160, 64], [64, 64, 0]]
palette_list2 = [
    [0, 0, 0],
    [128, 128, 0],
    [128, 0, 32],
    [128, 32, 0],
    [128, 0, 128],
    [64, 128, 32],
    [255, 255, 0],
    [255, 0, 0],
    [192, 128, 160],
    [0, 0, 255],
    [0, 128, 128],
    [64, 128, 160],
    [128, 160, 0],
    [0, 128, 0],
    [192, 128, 32],
    [128, 96, 128],
    [192, 0, 128],
    [0, 255, 0],
    [0, 224, 128],
    [128, 0, 0],
    [192, 0, 160],
    [64, 192, 64],
    [128, 128, 96],
    [128, 32, 128],
    [64, 0, 192],
]
palette_list3 = [
    [0, 0, 0],
    [229, 25, 74],
    [60, 179, 77],
    [255, 224, 25],
    [68, 99, 216],
    [245, 130, 49],
    [144, 30, 180],
    [68, 211, 245],
    [239, 50, 232],
    [191, 238, 70],
    [251, 189, 212],
    [128, 128, 0],
    [128, 0, 32],
    [128, 32, 0],
    [128, 0, 128],
    [64, 128, 32],
    [255, 255, 0],
    [255, 0, 0],
    [192, 128, 160],
    [0, 0, 255],
    [0, 128, 128],
    [64, 128, 160],
    [128, 160, 0],
    [0, 128, 0],
    [192, 128, 32],
    [128, 96, 128],
    [192, 0, 128],
    [0, 255, 0],
    [0, 224, 128],
    [128, 0, 0],
    [192, 0, 160],
    [64, 192, 64],
    [128, 128, 96],
    [128, 32, 128],
    [64, 0, 192],
]
palette_list4 = [[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
palette_list5 = [[0, 0, 0], [255, 0, 0], [0, 0, 255], [255, 0, 255], [255, 255, 0], [0, 255, 0]]
palette_list6 = [[0, 0, 0], [255, 255, 255]]
palette_list7 = [[0, 0, 0], [204, 102, 0], [255,0,0], [255, 255, 0], [0, 0, 255], [85,166,0], [93, 255, 255], [152, 102, 153]]


def add_palette_png(label_file, out_file):
    palette = np.array(palette_list1, dtype='uint8')
    # label = np.array(Image.open(label_file))  # 注意图片格式，读取方式可能需更改,所以推荐使用下面方式
    label = io.imread(label_file).squeeze()
    visualimg = Image.fromarray(label, "P")
    visualimg.putpalette(palette)
    visualimg.save(out_file, format='PNG')

def add_palette_tif(label_file, out_file):
    color_maps = {idx: i for idx, i in enumerate(palette_list4)}
    if label_file.endswith(('.tif', '.tiff', '.img')):
        with rio.open(label_file) as src:
            kwds = src.profile
            data0 = src.read(1)
        kwds.update(dict(dtype='uint8', count=1, nodata=0, compress='lzw'))
        out_raster = rio.open(out_file, 'w', **kwds)
        out_raster.write(data0, indexes=1)
        out_raster.write_colormap(1, color_maps)
        out_raster.close()
    else:
        data1 = io.imread(label_file)
        meta = {'driver': 'GTiff',
                'height': data1.shape[0],
                'width': data1.shape[1],
                'count': 1,
                'compress': 'lzw',
                'dtype': data1.dtype,}
        with rio.open(out_file, 'w', **meta) as dst:
            dst.write(data1, indexes=1)
            dst.write_colormap(1, color_maps)

def remove_color(label_file, out_file):
    data0 = io.imread(label_file, as_gray=True)
    io.imsave(out_file, data0, check_contrast=False)


if __name__ == "__main__":
    '''添加颜色表至tif图片'''
    lab_path = r'C:\Users\1\Desktop\遥感地物提取\Try2_output'
    out_path = r'C:\Users\1\Desktop\遥感地物提取\Try2_addcolor'
    label_files = sorted(glob(lab_path + '/*.tif'))
    os.makedirs(out_path, exist_ok=True)
    for label_file in tqdm(label_files):
        stem = os.path.splitext(os.path.basename(label_file))[0]
        out_file = os.path.join(out_path, stem + '.tif')
        add_palette_tif(label_file, out_file)
        # remove_color(label_file, out_file)
    
    '''添加颜色表至png图片'''
    # lab_path = r"/data1/zsc/data188/dfc25_track2_trainval/test/merge_prior_ensemble_orcls2_manual"
    # out_path = r"/data1/zsc/data188/dfc25_track2_trainval/test/merge_prior_ensemble_orcls2_manual_png"
    # label_files = sorted(glob(lab_path + '/*.jpg'))
    # os.makedirs(out_path, exist_ok=True)
    # for label_file in tqdm(label_files, ascii=True):
    #     name = os.path.basename(label_file)
    #     out_file = os.path.join(out_path, name).replace('.jpg', '.png')
    #     add_palette_png(label_file, out_file)


