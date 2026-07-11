# torch-config.py
import os
import torch

# 设置自定义路径
MODELS_DIR = "pretrained_models"

# 确保目录存在
os.makedirs(MODELS_DIR, exist_ok=True)

# 配置路径
os.environ['TORCH_HOME'] = MODELS_DIR
torch.hub.set_dir(MODELS_DIR)  # 显式设置hub目录

# 验证设置
print(f"[配置加载] PyTorch模型目录: {torch.hub.get_dir()}")