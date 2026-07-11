import datasets.transforms as T
from torchvision import transforms as TP

class SegmentationPresetTrain:
    def __init__(self,base_size, crop_size, mean, std, hflip_prob=0.5, vflip_prob=0.5):
        min_size = int(0.5 * base_size)
        max_size = int(1.2 * base_size)

        trans = [T.RandomResize(min_size, max_size)]
        if hflip_prob > 0:
            trans.append(T.RandomHorizontalFlip(hflip_prob))
        if vflip_prob > 0:
            trans.append(T.RandomVerticalFlip(vflip_prob))
        trans.extend([
            T.RandomCrop(crop_size),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ])
        self.transforms = T.Compose(trans)
    def __call__(self, img, target):
        return self.transforms(img, target)


class SegmentationPresetEval:
    def __init__(self, mean, std):
        self.transforms = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ])
    def __call__(self, img, target):
        return self.transforms(img, target)

class SegmentationPresetTest:
    def __init__(self, mean, std):
        self.transforms = TP.Compose([
            TP.ToTensor(),
            TP.Normalize(mean, std)
        ])
    def __call__(self, img):
        return self.transforms(img)

def get_transform(phase, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    base_size = 512
    crop_size = 512

    if phase == 'train':
        return SegmentationPresetTrain(base_size,crop_size,mean=mean,std=std)
    elif phase == 'val':
        return SegmentationPresetEval(mean=mean, std=std)
    else:
        return SegmentationPresetTest(mean=mean, std=std)