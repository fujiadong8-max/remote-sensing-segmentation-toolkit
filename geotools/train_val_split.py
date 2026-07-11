# -*- encoding:utf-8 -*-
import os
import random
import shutil
from glob import glob
from tqdm import tqdm


def train_split_val(datas_root):
    random.seed(2025)
    imgs_root = os.path.join(datas_root, 'images')
    labels_root = os.path.join(datas_root, 'labels')
    img_paths = sorted(glob(imgs_root + '/*.tif'))
    mask_paths = sorted(glob(labels_root + '/*.tif'))
    val = random.sample(range(len(mask_paths)), int(len(mask_paths) * 0.1))
    val_imgs = os.path.join(datas_root, 'val', 'images')
    val_labels = os.path.join(datas_root, 'val', 'labels')
    train_imgs = os.path.join(datas_root, 'train', 'images')
    train_labels = os.path.join(datas_root, 'train', 'labels')
    os.makedirs(val_imgs, exist_ok=True)
    os.makedirs(val_labels, exist_ok=True)
    os.makedirs(train_imgs, exist_ok=True)
    os.makedirs(train_labels, exist_ok=True)
    for i in tqdm(range(len(mask_paths))):
        ori_img = img_paths[i]
        ori_label = mask_paths[i]
        if i in val:
            shutil.copy(ori_img, val_imgs)
            shutil.copy(ori_label, val_labels)
        else:
            shutil.copy(ori_img, train_imgs)
            shutil.copy(ori_label, train_labels)


if __name__ == '__main__':
    datas_root = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains"
    train_split_val(datas_root)
