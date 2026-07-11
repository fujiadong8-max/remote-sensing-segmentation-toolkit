import os
from glob import glob
# from pathlib import Path
import numpy as np
import rasterio as rio
import torch
# from skimage import io
from tqdm import tqdm

# from collections import Counter
# os.environ['CUDA_VISIBLE_DEVICES'] = "3"
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"





def to_tensor(img):
    return torch.from_numpy(img.astype('f4'))


def main(args):
    gt_path = args.gt_path
    pr_path = args.pr_path
    if os.path.isdir(gt_path):
        gt_files = sorted(list(glob(gt_path + '/*.tif')))
    else:
        gt_files = [gt_path]
    if os.path.isdir(pr_path):
        pr_files = sorted(list(glob(pr_path + '/*.tif')))
    else:
        pr_files = [pr_path]

    assert len(gt_files) == len(pr_files), 'check files'

    device = torch.device(args.device)
    num_classes = args.num_classes + 1

    confusion_mat = torch.zeros((num_classes, num_classes),
                                dtype=torch.int64,
                                device=device)
    # sum_count = Counter()
    for idx in tqdm(range(len(gt_files))):
        with rio.open(str(gt_files[idx])) as src:
            data_gt = src.read(1)
            true_label = to_tensor(data_gt.flatten()).to(device)
        with rio.open(str(pr_files[idx])) as src:
            data_pr = src.read(1)
            # data_pr[data_pr > 0] = 1
            pred_label = to_tensor(data_pr.flatten()).to(device)
        # true_label = to_tensor(io.imread(str(gt_files[idx])).flatten()).to(device)
        # pred_label = to_tensor(io.imread(str(pr_files[idx])).flatten()).to(device)

        with torch.no_grad():
            mask = true_label != 255
            # pred_label = pred_label[mask]
            # true_label = true_label[mask]
            inds = num_classes * true_label[mask].to(
                torch.int64) + pred_label[mask].to(torch.int64)
            confusion_mat += torch.bincount(inds,
                                            minlength=num_classes**2).reshape(
                                                num_classes,
                                                num_classes)  # 横轴真实，纵轴预测(num_classes,num_classes)
    confusion_mat = confusion_mat.float()
    overall_acc = torch.diag(confusion_mat).sum() / confusion_mat.sum()
    precision = torch.diag(confusion_mat) / confusion_mat.sum(0)
    recall = torch.diag(confusion_mat) / confusion_mat.sum(1)  # 召回率，真是为正的样本中被标记为正的比例
    f1 = 2 * precision * recall / (precision + recall + 1e-6)
    iou = torch.diag(confusion_mat) / (confusion_mat.sum(1) + confusion_mat.sum(0) - torch.diag(confusion_mat))  # 交并比，模型对某一类别预测结果和真实值的交集与并集的比值，TP / (TP + FP + FN)

    dice = 2*torch.diag(confusion_mat) / (confusion_mat.sum(1) + confusion_mat.sum(0))
    mdice = np.nanmean(dice.cpu())
    miou = np.nanmean(iou.cpu())
    mrecall = np.nanmean(recall.cpu())
    mprecision = np.nanmean(precision.cpu())
    p0 = overall_acc
    pc = (confusion_mat.sum(1) * confusion_mat.sum(0)).sum() / (confusion_mat.sum())**2
    kappa = (p0 - pc) / (1 - pc)
    print(('OA:{:.2f}\n'
           'mIoU:{:.2f}\n'
           'mDice:{:.2f}\n'
           'mPrecision:{:.2f}\n'
           'mRecall:{:.2f}\n'           
           'Kappa:{:.2f}\n'
           'IoU:{}\n'
           'Dice:{}\n'
           'Precision:{}\n'
           'Recall:{}\n'
           'F1:{}').format(
               overall_acc * 100, miou * 100, mdice*100, mprecision * 100, mrecall * 100,
               kappa * 100, ['{:.2f}'.format(i) for i in (iou * 100).tolist()],
               ['{:.2f}'.format(i) for i in (dice * 100).tolist()],
               ['{:.2f}'.format(i) for i in (precision * 100).tolist()],
               ['{:.2f}'.format(i) for i in (recall * 100).tolist()],
               ['{:.2f}'.format(i) for i in (f1 * 100).tolist()]))


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--gt_path', type=str, default= r"D:\Data\test\test25提取结果精度评估\labels", help='true label path')
    parser.add_argument('--pr_path', type=str, default= r"D:\Data\test\test25提取结果精度评估\outputs", help='predict label path')
    parser.add_argument('--num_classes', type=int, default=4, help='number of classes')
    parser.add_argument('--device', type=str, default='cpu', help='device')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args)
