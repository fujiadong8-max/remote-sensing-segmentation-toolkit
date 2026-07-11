import re
import pandas as pd

def parse_log_file(file_path1, file_path2):
    nums = []
    for file_path in [file_path1, file_path2]:
        epochs = []
        global_correct = []
        precision = []
        recall = []
        f1_score = []
        iou = []
        loss = []
        dice = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line0 = line.strip()
                if 'epoch' in line0:
                    epochs.append(line0.split(':')[1].strip()[:-1])
                elif 'train_loss' in line0:
                    loss.append(line0.split(':')[1].strip())
                elif 'dice' in line0:
                    dice.append(line0.split(':')[1].strip())
                elif 'mean' in line0:
                    iou.append(line0.split(':')[1].strip())
                elif 'score' in line0:
                    f1_score.append(line0.split(':')[1].strip().split(',')[1].strip()[:-1].strip('\"\''))
                elif 'recall' in line0:
                    recall.append(line0.split(':')[1].strip().split(',')[1].strip()[:-1].strip('\"\''))
                elif 'precision' in line0:
                    precision.append(line0.split(':')[1].strip().split(',')[1].strip()[:-1].strip('\"\''))
                elif 'global correct' in line0:
                    global_correct.append(line0.split(':')[1].strip())
                else:
                    pass
        indic = {'global_correct':[float(i) for i in global_correct],
                'precision':[float(i) for i in precision],
                'recall':[float(i) for i in recall],
                'f1_score':[float(i) for i in f1_score],
                'iou':[float(i) for i in iou],
                'loss':[float(i) for i in loss],
                'dice':[float(i) for i in dice]}
        nums.append(indic)
    # print(nums)
    return nums




# 使用示例
if __name__ == "__main__":
    # 替换为你的日志文件路径
    log_file1 = r"C:\Users\24106\Desktop\示例数据\results20250520-111154.txt"
    log_file2 = r"C:\Users\24106\Desktop\示例数据\results20250430-012318.txt"
    df = parse_log_file(log_file1, log_file2)
