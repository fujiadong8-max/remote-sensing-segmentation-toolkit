import os
from PIL import Image
from torch.utils.data import Dataset
from glob import glob
from skimage import io


class CustomDataset(Dataset):

    def __init__(self, root: str, train: bool, transforms=None):
        super(CustomDataset, self).__init__()
        self.flag = "train" if train else "val"
        data_root = os.path.join(root, self.flag)
        assert os.path.exists(data_root), f"path '{data_root}' does not exists."
        self.transforms = transforms
        self.img_list1 = glob(os.path.join(data_root, "images", "*.tif"))
        self.lab_list1 = glob(os.path.join(data_root, "labels", "*.tif"))
        self.img_list = sorted(self.img_list1)
        self.lab_list = sorted(self.lab_list1)
        assert len(self.img_list) == len(self.lab_list)

    def __getitem__(self, idx):
        img = io.imread(self.img_list[idx])
        lab = io.imread(self.lab_list[idx])
        #img = img[:, :, :3]
        # 这里转回PIL的原因是，transforms中是对PIL数据进行处理
        img = Image.fromarray(img)
        lab = Image.fromarray(lab)

        if self.transforms is not None:
            img, lab = self.transforms(img, lab)

        return img, lab

    def __len__(self):
        return len(self.img_list)

class TestDataset(Dataset):
    def __init__(self, root: str, transforms=None):
        super(TestDataset, self).__init__()
        assert os.path.exists(root), f"path '{root}' does not exists."
        self.transforms = transforms
        self.img_list = sorted(glob(root +  "/*.tif"))

    def __getitem__(self, idx):
        img = io.imread(self.img_list[idx])
        img_name = os.path.basename(self.img_list[idx])

        img = Image.fromarray(img)

        if self.transforms is not None:
            img = self.transforms(img)

        return img, img_name

    def __len__(self):
        return len(self.img_list)


#     @staticmethod
#     def collate_fn(batch):
#         images, targets = list(zip(*batch))
#         batched_imgs = cat_list(images, fill_value=0)
#         batched_targets = cat_list(targets, fill_value=255)
#         return batched_imgs, batched_targets


# def cat_list(images, fill_value=0):
#     max_size = tuple(max(s) for s in zip(*[img.shape for img in images]))
#     batch_shape = (len(images),) + max_size
#     batched_imgs = images[0].new(*batch_shape).fill_(fill_value)
#     for img, pad_img in zip(images, batched_imgs):
#         pad_img[..., :img.shape[-2], :img.shape[-1]].copy_(img)
#     return batched_imgs
