# -*- coding: utf-8 -*-
import os
import rasterio as rio
from tqdm import tqdm
from glob import glob


def slid_clip(img_file, img_save, block_xsize, block_ysize, slide_xsize, slide_ysize, has_tail=False, is_label=False):
    with rio.open(img_file) as src:
        meta = src.profile
        w, h = src.width, src.height
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
                # y0 = h - block_ysize
                # y_list.append(y0)
                # break
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
                # x0 = w - block_xsize
                # x_list.append(x0)
                # break
        clip_datas = [[y, x] for y in y_list for x in x_list]
        # print(clip_datas)
        for (y0, y1), (x0, x1) in tqdm(clip_datas):
            meta.update({
                'height': y1 - y0,
                'width': x1 - x0,
                'transform': src.window_transform(((y0, y1), (x0, x1)))
            })
            out_file = os.path.join(img_save, os.path.basename(img_file).replace('.tif', '_{}_{}.tif'.format(str(y0), str(x0))))
            with rio.open(out_file, 'w', **meta) as dst:
                dst.write(src.read(window=((y0, y1), (x0, x1))))
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
    img_path = r'/data1/zsc/data122/zsc/data177/Massachusetts_Roads/train/labels' # 待切分的大图路径，根据自己需求修改
    img_save = r'/data1/zsc/data122/zsc/data177/Massachusetts_Roads/train_512/labels'  # 切分后的小图保存路径，根据自己需求修改
    os.makedirs(img_save, exist_ok=True)
    img_files = glob(img_path + '/*.tif')
    block_xsize = 512  # 切图的行大小
    block_ysize = 512  # 切图的列大小
    slide_xsize = 512  # 滑动行步长
    slide_ysize = 512  # 滑动列步长
    has_tail = True  # 是否保留尾部不足一块的图
    is_label = True  # 裁剪影像是否为标签，如果是标签为true，如果为原图影像为False。
    for img_file in tqdm(img_files):
        slid_clip(img_file, img_save, block_xsize, block_ysize, slide_xsize, slide_ysize, has_tail, is_label)