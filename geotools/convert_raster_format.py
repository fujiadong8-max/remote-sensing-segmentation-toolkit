# -*- coding: utf-8 -*-

import os
from glob import glob
from skimage import io
from tqdm import tqdm


def change_type(label_file, out_file):
    data0 = io.imread(label_file)
    io.imsave(out_file, data0, check_contrast=False)

if __name__ == '__main__':
    old_type = '.tif'
    new_type = '.png'
    lab_path = r"C:\Users\1\Desktop\遥感地物提取\test_data_2024\images"
    out_path = r"C:\Users\1\Desktop\遥感地物提取\test_data_2024\images_png"
    label_files = sorted(glob(lab_path + '/*{}'.format(old_type)))
    os.makedirs(out_path, exist_ok=True)
    for label_file in tqdm(label_files):
        name = os.path.basename(label_file)
        out_file = os.path.join(out_path, name).replace(old_type, new_type)
        change_type(label_file, out_file)


