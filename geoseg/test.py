import os
import argparse
import numpy as np
from glob import glob
from tqdm import tqdm
import torch
from models import create_model
from skimage import io
import utils.distributed_utils as utils
from datasets import TestDataset, get_transform

def main(args):
    num_classes = args.num_classes + 1
    weight_path = args.weight_path
    img_path = args.img_path
    out_path = args.out_path
    lab_path = args.lab_path
    os.makedirs(out_path, exist_ok=True)
    
    mean = (0.37241595, 0.38033836, 0.37343018)
    std = (0.22653883, 0.2187654,  0.22268369)
    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(model_name='segformer', num_classes=num_classes)
    model.load_state_dict(torch.load(weight_path, map_location='cpu')['model'])
    model.to(device)

    test_dataset = TestDataset(img_path, transforms=get_transform(phase='test', mean=mean, std=std))
    test_loader = torch.utils.data.DataLoader(test_dataset,
                                            batch_size=1,
                                            num_workers=0,
                                            pin_memory=True)
    model.eval()
    with torch.no_grad():
        for image, image_name in tqdm(test_loader):
            image = image.to(device)
            output = model(image)
            pred_mask = output.argmax(1).squeeze().cpu().numpy().astype(np.uint8)
            # pred_mask[pred_mask == 1] = 255
            out_file = os.path.join(out_path, image_name[0])
            io.imsave(out_file, pred_mask, check_contrast=False)
    
    if lab_path is not None:
        confmat = utils.ConfusionMatrix(num_classes)
        lab_files = sorted(glob(lab_path + '/*.tif'))
        for lab_file in tqdm(lab_files):
            name  = os.path.basename(lab_file)
            out_file = os.path.join(out_path, name)
            lab_mask = io.imread(lab_file)
            out_mask = io.imread(out_file)
            lab_tensor = torch.from_numpy(lab_mask)
            out_tensor = torch.from_numpy(out_mask)
            confmat.update(lab_tensor.to(device).flatten(), out_tensor.to(device).flatten())
        confmat.reduce_from_all_processes()
        val_info = str(confmat)
        print(val_info)
        out_file = os.path.join(out_path, 'results.txt')
        with open(out_file, "w") as f:
            f.write(val_info + "\n\n")

def parse_args():
    parser = argparse.ArgumentParser(description="pytorch training")
    parser.add_argument("--weight-path", type=str, default="./work_dirs/features_segformer_22/best_model.pth", help="weights path")
    parser.add_argument("--img-path", type=str, default="/data1/zsc/data/project/trains/val/images", help="需要预测的图片所在文件夹")
    parser.add_argument("--out-path", type=str, default="/data1/zsc/data/project/trains/val/outs4", help="预测结果保留的文件夹")
    parser.add_argument("--lab-path", type=str, default="/data1/zsc/data/project/trains/val/labels", help="预测图片对应的标签所在文件夹")
    parser.add_argument("--num-classes", default=4, type=int)
    parser.add_argument("--device", type=str, default="cuda", help="training device")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)