from glob import glob
import os
from tqdm import tqdm
import subprocess



def to_shp(src_file, dst_file):
    try:
        # 构造 ogr2ogr 命令
        ogr_cmd = [
            'ogr2ogr', '-lco', 'ENCODING=UTF-8', '-f', 'ESRI Shapefile', dst_file, src_file
        ]

        # 执行 ogr2ogr 命令
        subprocess.run(ogr_cmd, check=True)

        print(f"转换成功：{src_file} 转换为 {dst_file}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{e}")

def to_kml(src_file, dst_file):
    try:
        # 构造 ogr2ogr 命令
        ogr_cmd = [
            'ogr2ogr', '-lco', 'ENCODING=UTF-8', '-f', 'KML', dst_file, src_file
        ]

        # 执行 ogr2ogr 命令
        subprocess.run(ogr_cmd, check=True)

        print(f"转换成功：{src_file} 转换为 {dst_file}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{e}")

def to_json(src_file, dst_file):
    try:
        # 构造 ogr2ogr 命令
        ogr_cmd = [
            'ogr2ogr', '-lco', 'ENCODING=UTF-8', '-f', 'GeoJSON', dst_file, src_file
        ]

        # 执行 ogr2ogr 命令
        subprocess.run(ogr_cmd, check=True)

        print(f"转换成功：{src_file} 转换为 {dst_file}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{e}")

def convert_type(src_file, dst_file):
    if dst_file.endswith('.shp'):
        to_shp(src_file, dst_file)
    elif dst_file.endswith('.kml'):
        to_kml(src_file, dst_file)
    elif dst_file.endswith(('.json', '.geojson')):
        to_json(src_file, dst_file)
    else:
        print("文件类型不匹配，请检查文件类型。")


if __name__ == "__main__":
    old_type = '.json'
    new_type = '.kml'
    src_path = r"D:\Data\unknown\json"
    dst_path = r"D:\Data\unknown\kml"
    os.makedirs(dst_path, exist_ok=True)
    src_files = glob(src_path + '/*{}'.format(old_type))
    for src_file in tqdm(src_files):
        name = os.path.basename(src_file)
        dst_file = os.path.join(dst_path, name.replace('{}'.format(old_type), '{}'.format(new_type)))
        convert_type(src_file, dst_file)

