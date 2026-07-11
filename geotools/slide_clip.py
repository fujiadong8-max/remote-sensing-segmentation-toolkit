# -*- coding: utf-8 -*-
import os
import rasterio as rio
from tqdm import tqdm
from glob import glob


def slid_clip(img_file, img_save, block_xsize, block_ysize, slide_xsize, slide_ysize, has_tail=False, is_label=False):
    with rio.open(img_file) as src:
        meta = src.profile
        w, h = src.width, src.height
        #从上到下
        y_list = []
        for y0 in range(0, h, slide_ysize):
            if y0 + block_ysize < h:
                y_list.append([y0, y0 + block_ysize])
            else:
                if has_tail:
                    y_list.append([y0, h])
                    break
                else:
                    break
        #从左到右
        x_list = []
        for x0 in range(0, w, slide_xsize):
            if x0 + block_xsize < w:
                x_list.append([x0, x0 + block_xsize])
            else:
                if has_tail:
                    x_list.append([x0, w])
                    break
                else:
                    break
        clip_datas = [[y, x] for y in y_list for x in x_list]
        for (y0, y1), (x0, x1) in tqdm(clip_datas):
            meta.update({
                'height': y1 - y0,
                'width': x1 - x0,
                'transform': src.window_transform(((y0, y1), (x0, x1))),
                'BIGTIFF':'YES',
            })
            out_file = os.path.join(img_save, os.path.basename(img_file).replace('.tif', '_{}_{}.tif'.format(str(y0), str(x0))))
            with rio.open(out_file, 'w', **meta) as dst:
                data0 = src.read(window=((y0, y1), (x0, x1)))
                dst.write(data0)
                if is_label:
                    color_maps = {
                    1: (255, 0, 0),
                    2: (0, 255, 0),
                    3: (0, 0, 255),
                    4: (255, 255, 0),
                    5: (255, 0, 255),
                    6: (0, 255, 255),
                    7: (100, 255, 0),
                    8: (0, 255, 100)
                    }
                    dst.write_colormap(1, color_maps)

if __name__ == "__main__":
    img_path = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\masks" # 待切分的大图路径，根据自己需求修改
    img_save = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\masks\clips"  # 切分后的小图保存路径，根据自己需求修改
    os.makedirs(img_save, exist_ok=True)
    img_files = glob(img_path + '/*YRD_2024.tif')
    block_xsize = 1024  # 切图的行大小1024
    block_ysize = 1024  # 切图的列大小1024
    slide_xsize = 1024  # 滑动行步长1024
    slide_ysize = 1024  # 滑动列步长1024
    has_tail = False   # 是否保留尾部不足一块的图
    is_label = True     # 裁剪影像是否为标签，如果是标签为True，如果为原图影像为False。
    for img_file in tqdm(img_files):
        slid_clip(img_file, img_save, block_xsize, block_ysize, slide_xsize, slide_ysize, has_tail, is_label)