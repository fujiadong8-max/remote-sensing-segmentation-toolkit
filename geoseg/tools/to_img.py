import numpy as np
import matplotlib.pyplot as plt
from to_excel import parse_log_file


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

log_file1 = r"C:\Users\24106\Desktop\示例数据\results20250520-111154.txt"
log_file2 = r"C:\Users\24106\Desktop\示例数据\results20250430-012318.txt"
df = parse_log_file(log_file1, log_file2)
# print(df[1])
global_correct = {'U-Net':df[0]['global_correct'], 'VGG16-UNet':df[1]['global_correct']}
precision = {'U-Net':df[0]['precision'], 'VGG16-UNet':df[1]['precision']}
recall = {'U-Net':df[0]['recall'], 'VGG16-UNet':df[1]['recall']}
f1_score = {'U-Net':df[0]['f1_score'], 'VGG16-UNet':df[1]['f1_score']}
iou = {'U-Net':df[0]['iou'], 'VGG16-UNet':df[1]['iou']}
loss = {'U-Net':df[0]['loss'], 'VGG16-UNet':df[1]['loss']}
dice = {'U-Net':df[0]['dice'], 'VGG16-UNet':df[1]['dice']}
# 设置全局样式
plt.rcParams.update({
    'font.family': 'SimSun',  # 中文字体
    'axes.edgecolor': '#4A4A4A',
    'axes.linewidth': 1.2,
    'grid.color': '#DCDCDC',
    'grid.linestyle': '--'
})

# 生成模拟数据
epochs = np.arange(0, 50)
models = [
    ('SegNet_F1score', 0.45, 0.02),
    ('Dilation-Segnet (A)_F1score', 0.48, 0.018),
    ('Dilation-Segnet (B)_Flscore', 0.52, 0.022),
    ('Dilation-Segnet (C)_Flscore', 0.55, 0.025),
    ('Dilation-Segnet (D)_Flscore', 0.58, 0.024),
    ('Dilation-Segnet (E)_Flscore', 0.62, 0.027),
    ('Dilation-Segnet (F)_Flscore', 0.65, 0.026)
]

# 创建带屏幕效果的画布
fig = plt.figure(figsize=(12, 8), facecolor='#F0F0F0')
ax = fig.add_axes([0.08, 0.12, 0.85, 0.75], facecolor='white')

# 绘制曲线
# line_styles = ['-', '--', '-.', ':']*2
line_styles = ['-', '-']
# colors = ['#E64A45', '#4E79A7', '#59A14F', '#EDC948', '#B07AA1', '#76B7B2', '#FF9DA7']
colors = ['#E64A45', '#59A14F']
i = 0
for key, values in loss.items():
# for i, (label, base, noise) in enumerate(models):
    # noise = np.random.normal(0, noise, len(epochs))
    # trend = 0.6 * (1 - np.exp(-epochs/30)) + base
    # values = np.clip(trend + noise, 0, 0.7)
    # print(epochs)
    # print(values)
    ax.plot(epochs, values, 
            linestyle=line_styles[i],
            linewidth=2.5,
            color=colors[i],
            alpha=0.9,
            label=key)
    i += 1

# 坐标轴设置
ax.set_xlim(0, 50)
# ax.set_ylim(30, 100)
ax.set_xlabel('Epoch', fontsize=19, labelpad=10)
ax.set_ylabel('Loss', fontsize=19, labelpad=10)
# ax.xaxis.set_major_locator(MultipleLocator(20))
# ax.xaxis.set_minor_locator(MultipleLocator(5))
# ax.yaxis.set_major_locator(MultipleLocator(0.1))
# ax.yaxis.set_minor_locator(MultipleLocator(0.05))

# 添加网格
# ax.grid(True, which='major', alpha=0.6)
# ax.grid(True, which='minor', alpha=0.3)

# 添加图例
# 修改图例部分代码（替换原有legend部分）
legend = ax.legend(
    loc='lower right',           # 定位在右上方
    frameon=True,                # 保留边框
    facecolor='white',           # 背景色
    edgecolor='#4A4A4A',         # 边框颜色与轴线统一
    fontsize=19,                 # 缩小字号
    # ncol=2,                     # 分两列显示
    borderpad=0.8,              # 边距压缩
    columnspacing=1.2,          # 列间距调整
    handlelength=2.0,           # 图例线长缩短
    bbox_to_anchor=(1, 0) # 精确微调位置
)

# 同步调整子图区域避免截断（修改add_axes参数）
# ax = fig.add_axes([0.10, 0.12, 0.82, 0.75])  # 右侧留出更多空间
legend.get_frame().set_linewidth(1.2)

# 添加屏幕仿真元素
ax.text(102, 0.72, '神经网络的建筑物变化检测方法设计论文.pdf', 
        ha='right', va='bottom', color='#666666', fontsize=10)
ax.text(50, -0.15, '36/48', ha='center', va='top', color='#4A4A4A', fontsize=12)
ax.text(102, -0.15, 'DEL', ha='right', va='top', color='#4A4A4A', fontsize=12)

# 添加图表标题
# plt.figtext(0.5, 0.95, 'sar水体提取模型训练指标', 
#            ha='center', va='top', fontsize=14, color='#2B2B2B')

# 添加屏幕边框效果
for spine in ax.spines.values():
    spine.set_zorder(10)

# 显示图表
plt.show()

# 保存文件（取消注释使用）
# fig.savefig('SegNet_F1score.png', dpi=300, bbox_inches='tight', facecolor='#F0F0F0')