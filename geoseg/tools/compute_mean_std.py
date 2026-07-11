r'''
import os
from PIL import Image
import numpy as np
from tqdm import tqdm



def main():
    img_channels = 3
    img_dir = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains\images"
    roi_dir = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains\labels"
    assert os.path.exists(img_dir), f"image dir: '{img_dir}' does not exist."
    assert os.path.exists(roi_dir), f"roi dir: '{roi_dir}' does not exist."

    img_name_list = [i for i in os.listdir(img_dir) if i.endswith(".png")]
    cumulative_mean = np.zeros(img_channels)
    cumulative_std = np.zeros(img_channels)
    for img_name in tqdm(img_name_list):
        img_path = os.path.join(img_dir, img_name)
        ori_path = os.path.join(roi_dir, img_name)
        img0 = np.array(Image.open(img_path)) / 255.
        img = img0.reshape((-1, img0.shape[-1]))
        # print(img.mean(axis=0))
        # roi_img = np.array(Image.open(ori_path).convert('L'))
        # print(img.shape)
        # img = img[roi_img != 11]
        # print(img.shape)
        # quit()
        cumulative_mean += img.mean(axis=0)
        cumulative_std += img.std(axis=0)

    mean = cumulative_mean / len(img_name_list)
    std = cumulative_std / len(img_name_list)
    print(f"mean: {mean}")
    print(f"std: {std}")


if __name__ == '__main__':
    main()
r'''

import os
import numpy as np
import rasterio as rio
from tqdm import tqdm

def main():
    # 1. 路径配置
    img_dir = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains\images"
    roi_dir = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains\labels" 
    
    if not os.path.exists(img_dir) or not os.path.exists(roi_dir):
        print("错误: 影像或标签路径不存在。")
        return

    img_name_list = [i for i in os.listdir(img_dir) if i.endswith(".tif")]
    
    with rio.open(os.path.join(img_dir, img_name_list[0])) as tmp:
        img_channels = tmp.count

    # 用列表存储所有有效像素，最后统一计算（如果内存允许）
    # 或者采用增量统计
    all_valid_pixels = []
    
    # 2. 遍历计算
    for img_name in tqdm(img_name_list, desc="正在分析有标签区域"):
        img_path = os.path.join(img_dir, img_name)
        mask_path = os.path.join(roi_dir, img_name)
        
        if not os.path.exists(mask_path):
            continue

        with rio.open(img_path) as src, rio.open(mask_path) as m_src:
            # 读取影像 (C, H, W)
            img0 = src.read().astype(np.float32)
            # 读取标签 (1, H, W)
            mask = m_src.read(1)
            
            # 处理影像异常值
            img0 = np.nan_to_num(img0, nan=0.0, posinf=0.0, neginf=0.0)
            img0[img0 < -1e10] = 0 
            
            if img0.max() > 1.1:
                img0 /= 255.0
            
            # 转换为 (H, W, C)
            img_hwc = img0.transpose(1, 2, 0)
            
            # --- 关键逻辑：提取有标签的像素 ---
            # 找出 mask 中大于 0 的索引
            valid_mask = mask > 0
            
            # 只取有标签部分的像素点，形状变为 (N_valid_pixels, C)
            roi_pixels = img_hwc[valid_mask]
            
            if roi_pixels.size > 0:
                all_valid_pixels.append(roi_pixels)

    if not all_valid_pixels:
        print("警告：未发现任何带有有效标签的像素！")
        return

    # 将所有图片的有效像素合并
    combined_pixels = np.concatenate(all_valid_pixels, axis=0)
    
    # 3. 计算最终结果
    mean = combined_pixels.mean(axis=0)
    std = combined_pixels.std(axis=0)
    
    print("\n--- 仅针对【有标签区域】的计算结果 ---")
    print(f"参与计算的有效像素总数: {combined_pixels.shape[0]}")
    print(f"Mean (各通道): {mean}")
    print(f"Std  (各通道): {std}")
    print(f"\n建议 Normalize 参数: mean={list(mean.round(4))}, std={list(std.round(4))}")

if __name__ == '__main__':
    main()
