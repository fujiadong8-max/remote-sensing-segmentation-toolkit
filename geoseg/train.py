import torchhub
import os
import time
import argparse
import datetime
import torch
from utils import train_one_epoch, evaluate, create_lr_scheduler
from datasets import CustomDataset, get_transform
from models import create_model
import numpy as np

def main(args):
    os.makedirs(args.weight_path, exist_ok=True)
    results_file = os.path.join(args.weight_path, "results{}.txt".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    batch_size = args.batch_size
    num_classes = args.num_classes + 1

    # 使用 tools/compute_mean_std.py 文件运行后的计算结果写在这里
    mean = (0.48866168, 0.3827826, 0.30538547, 0.60189563)
    std = (0.20415, 0.1784638, 0.14975975, 0.38790965)

    train_dataset = CustomDataset(args.data_path, train=True, transforms=get_transform(phase='train', mean=mean, std=std))
    val_dataset = CustomDataset(args.data_path, train=False, transforms=get_transform(phase='val', mean=mean, std=std))
    num_workers = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
    train_loader = torch.utils.data.DataLoader(train_dataset,
                                                batch_size=batch_size,
                                                num_workers=num_workers,
                                                shuffle=True,
                                                pin_memory=True)

    val_loader = torch.utils.data.DataLoader(val_dataset,
                                             batch_size=1,
                                             num_workers=num_workers,
                                             pin_memory=True)

    model = create_model(model_name='unet', num_classes=num_classes)
    model.to(device)

    params_to_optimize = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params_to_optimize,
                                lr=args.lr,
                                momentum=args.momentum,
                                weight_decay=args.weight_decay)

    scaler = torch.amp.GradScaler('cuda') if args.amp else None

    # 创建学习率更新策略，这里是每个step更新一次(不是每个epoch)
    lr_scheduler = create_lr_scheduler(optimizer,
                                       len(train_loader),
                                       args.epochs,
                                       warmup=True)

    if args.resume:
        checkpoint = torch.load(args.resume, map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
        args.start_epoch = checkpoint['epoch'] + 1
        if args.amp:
            scaler.load_state_dict(checkpoint["scaler"])

    best_dice = 0.
    start_time = time.time()
    for epoch in range(args.start_epoch, args.epochs):
        mean_loss, lr = train_one_epoch(model,
                                        optimizer,
                                        train_loader,
                                        device,
                                        epoch,
                                        num_classes,
                                        lr_scheduler=lr_scheduler,
                                        print_freq=args.print_freq,
                                        scaler=scaler)

        confmat, dice = evaluate(model,
                                 val_loader,
                                 device=device,
                                 num_classes=num_classes)
        val_info = str(confmat)
        print(val_info)
        print(f"dice coefficient: {dice:.3f}")
        # write into txt
        with open(results_file, "a") as f:
            # 记录每个epoch对应的train_loss、lr以及验证集各指标
            train_info = f"[epoch: {epoch}]\n" \
                         f"train_loss: {mean_loss:.4f}\n" \
                         f"lr: {lr:.6f}\n" \
                         f"dice coefficient: {dice:.3f}\n"
            f.write(train_info + val_info + "\n\n")

        if args.save_best is True:
            if best_dice < dice:
                best_dice = dice
            else:
                continue

        save_file = {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "lr_scheduler": lr_scheduler.state_dict(),
            "epoch": epoch,
            "args": args
        }
        if args.amp:
            save_file["scaler"] = scaler.state_dict()

        if args.save_best is True:
            torch.save(save_file, "{}/best_model.pth".format(args.weight_path))
        else:
            torch.save(save_file, "{}/model_{}.pth".format(args.weight_path, epoch))

    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    print("training time {}".format(total_time_str))


def parse_args():
    parser = argparse.ArgumentParser(description="pytorch training")
    parser.add_argument("--data-path",default=r"C:\Users\1\Desktop\遥感地物提取\test data 2024\trains",help="datastes root")
    parser.add_argument("--weight-path",default=r"C:\Users\1\Desktop\遥感地物提取\test data 2024\ Work_dirs\features_unet_1",help="save weights path")

    parser.add_argument("--num-classes", default=6, type=int, help="number of classes, exclude background")
    parser.add_argument("--device", default="cuda:0", help="training device")
    parser.add_argument("-b", "--batch-size", default=4, type=int)
    parser.add_argument("--epochs",default=50,type=int,metavar="N",help="number of total epochs to train")
    parser.add_argument('--lr',default=0.01,type=float,help='initial learning rate')
    parser.add_argument('--momentum',default=0.9,type=float,metavar='M',help='momentum')
    parser.add_argument('--wd','--weight-decay',default=1e-4,type=float,metavar='W',help='weight decay (default: 1e-4)',dest='weight_decay')
    parser.add_argument('--print-freq',default=1,type=int,help='print frequency')
    parser.add_argument('--resume', default='', help='resume from checkpoint')
    parser.add_argument('--start-epoch',default=0,type=int,metavar='N',help='start epoch')
    parser.add_argument('--save-best',default=True,type=bool,help='only save best dice weights')
    # Mixed precision training parameters
    parser.add_argument("--amp",default=False,type=bool,help="Use torch.cuda.amp for mixed precision training")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)
