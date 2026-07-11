
import os
from glob import glob
import rasterio

def merge_bands(input_folder, output_path):
    # 查找目标波段文件（兼容不同命名格式）
    band_files = {
        'B02': ['B02_10m', 'B02.tif', 'B02_*.jp2'],
        'B03': ['B03_10m', 'B03.tif', 'B03_*.jp2'],
        'B04': ['B04_10m', 'B04.tif', 'B04_*.jp2'],
        # 'B08': ['B08_10m', 'B08.tif', 'B08_*.jp2']
    }
    found_bands = {}
    for band, patterns in band_files.items():
        for pattern in patterns:
            files = glob(os.path.join(input_folder, '**', f'*{pattern}*'), recursive=True)
            if files:
                found_bands[band] = files[0]
                break

    # 按顺序读取波段数据（蓝、绿、红、近红外）
    # bands_order = ['B02', 'B03', 'B04', 'B08']
    bands_order = ['B02', 'B03', 'B04']
    band_data = []
    for band in bands_order:
        with rasterio.open(found_bands[band]) as src:
            band_data.append(src.read(1))  # 读取第一波段

    # 获取参考元数据（坐标系、变换矩阵等）
    with rasterio.open(found_bands['B02']) as template:
        meta = template.meta
        meta.update(count=3, dtype='uint16', compress='lzw')  # 更新为3波段

    # 写入多波段文件
    with rasterio.open(output_path, 'w', **meta) as dst:
        for i, data in enumerate(band_data, start=1):
            dst.write(data, i)  # 按顺序写入波段

if __name__ == "__main__":
    src_path = r"D:\Data\test\test07波段合并\S2A_52UEV_20240814_0_L2A"
    out_file = r"D:\Data\test\test07波段合并\S2A_52UEV_20240814_0_L2A_merge\merged.tif"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    merge_bands(src_path, out_file)