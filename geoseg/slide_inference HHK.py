
from pathlib import Path
from tqdm import tqdm
from math import ceil
from raster_inference import RasterSampleDataset
import os
import rasterio as rio
import argparse
import numpy as np
from glob import glob
import torch
from models import create_model

def slide_infer(src_file, dst_file, model, win_size, step_size, pad_size, device):
    mean = (0.37241595, 0.38033836, 0.37343018)
    std  = (0.22653883, 0.2187654,  0.22268369)
    src_file = Path(src_file)
    dataset = RasterSampleDataset(src_file,
                                win_size=win_size,
                                step_size=step_size,
                                pad_size=pad_size,
                                need_tail=True,                                
                                band_index=[1, 2, 3],  # 尝试修改
                                to_type='uint8')
    kwds = dataset.meta
    kwds.update(driver='GTiff', count=1, dtype='uint8', nodata=0, compress='lzw')
    # kwds.update(driver='GTiff', count=1, dtype='uint8', nodata=0, compress='lzw', BIGTIFF='YES')
    out_raster = rio.open(dst_file, 'w', **kwds)
    color_maps = {1:[255, 0, 0], 2:[0, 255, 0], 3:[0, 0, 255], 4:[255, 255, 0]}
    out_raster.write_colormap(1, color_maps)
    padh, padw = dataset.pad_size
    col_nums = ceil(dataset.width / win_size)
    temp_list = []
    prog_bar = tqdm(total=len(dataset), desc=src_file.name)
    model.eval()
    with torch.no_grad():
        for i, (img, top_x, top_y, down_x, down_y) in enumerate(dataset):
            img = (img / 255.0 - mean) / std
            img = torch.from_numpy(img).to(device="cuda", dtype=torch.float32)
            img = img.unsqueeze(0).permute(0, 3, 1, 2)
            output = model(img).argmax(1).squeeze().cpu().numpy().astype(np.uint8)
            winw, winh = down_x - top_x, down_y - top_y
            output = output[padh:win_size+padh, padw:win_size+padw]
            output = output[:winh, :winw]
            temp_list.append(output)
            if (i + 1) % col_nums == 0:
                temp_data = np.hstack(temp_list)
                write_window = rio.windows.Window(0, top_y, dataset.width, winh)
                out_raster.write(temp_data, indexes=1, window=write_window)
                temp_list = []
            prog_bar.update()
    out_raster.close()
def main(args):
    weight_path = args.weight_path
    img_path = args.img_path
    out_path = args.out_path
    os.makedirs(out_path, exist_ok=True)
    num_classes = args.num_classes + 1
    win_size = args.win_size
    step_size = args.step_size
    pad_size = args.pad_size
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = create_model(model_name='segformer', num_classes=num_classes)
    model.load_state_dict(torch.load(weight_path, map_location='cpu', weights_only=False)['model'])
    model.to(device)
    img_files = sorted(glob(os.path.join(img_path, '*.tif')))
    for img_file in img_files:
        image_name = os.path.basename(img_file)
        out_file = os.path.join(out_path, image_name)
        slide_infer(img_file, out_file, model, win_size, step_size, pad_size, device)

def parse_args():
    parser = argparse.ArgumentParser(description="pytorch inference")
    parser.add_argument("--weight-path", type=str, default=r"geoseg\work_dirs\features_segformer_22\best_model.pth", help="weights path")
    parser.add_argument("--img-path", type=str, default=r"C:\Users\1\Desktop\遥感地物提取\Try1", help="需要预测的图片所在文件夹")
    parser.add_argument("--out-path", type=str, default=r"C:\Users\1\Desktop\遥感地物提取\output", help="预测结果保留的文件夹")
    parser.add_argument("--num-classes", default=4, type=int)
    parser.add_argument("--win-size", type=int, default=500, help="window size")
    parser.add_argument("--step-size", type=int, default=512, help="step size")
    parser.add_argument("--pad-size", type=int, default=6, help="padding size")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    main(args)




