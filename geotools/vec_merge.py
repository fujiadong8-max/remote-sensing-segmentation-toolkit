# import os
import fiona


def merge_vector_files(shp_path1, shp_path2, shp_save_path):
    geo_list = []
    with fiona.open(shp_path1) as src1:
        meta = src1.meta
        for i in src1:
            geo_list.append(i)
    with fiona.open(shp_path2) as src2:
        for j in src2:
            geo_list.append(j)

    with fiona.open(shp_save_path, mode='w', **meta) as layer:
        for i in geo_list:
            layer.write(i)

if __name__ == "__main__":
    shp_path1 = r"D:\Data\test\test12多矢量文件合并\bql.shp"
    shp_path2 = r"D:\Data\test\test12多矢量文件合并\bql2.shp"
    shp_save_path = r"D:\Data\test\test12多矢量文件合并\bql3333.shp"
    merge_vector_files(shp_path1, shp_path2, shp_save_path)

