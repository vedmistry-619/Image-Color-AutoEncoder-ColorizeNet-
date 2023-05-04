import torch
from torchvision import transforms, datasets
import numpy as np
from PIL import Image
from skimage.color import rgb2lab, rgb2gray, lab2rgb


def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


class GrayscaleImageFolder(datasets.ImageFolder):
    def __getitem__(self, index):
        path, target = self.imgs[index]
        img = self.loader(path)
        if self.transform is not None:
            img_orig = self.transform(img)
            img_orig = np.asarray(img_orig)
            img_lab = rgb2lab(img_orig)  #CONVERT RGB to LAB
            img_ab = img_lab[:, :, 1:3]
            img_ab = (img_ab + 128) / 255
            img_ab = torch.from_numpy(img_ab.transpose((2, 0, 1))).float()
            img_orig = rgb2gray(img_orig)
            img_orig = torch.from_numpy(img_orig).unsqueeze(0).float()

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img_orig, img_ab, target


def load_gray(path, max_size=360, shape=None):
    img_gray = Image.open(path).convert('L')

    if max(img_gray.size) > max_size:
        size = max_size
    else:
        size = max(img_gray.size)

    if shape is not None:
        size = shape

    img_transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor()
    ])

    img_gray = img_transform(img_gray).unsqueeze(0)
    return img_gray


def to_rgb(img_l, img_ab):
    if img_l.shape == img_ab.shape:
        img_lab = torch.cat((img_l, img_ab), 1).numpy().squeeze()
    else:
        img_lab = torch.cat(
            (img_l, img_ab[:, :, :img_l.size(2), :img_l.size(3)]),
            dim=1
        ).numpy().squeeze()

    img_lab = img_lab.transpose(1, 2, 0)
    img_lab[:, :, 0] = img_lab[:, :, 0] * 100  #RANGE PIXEL 0-100
    img_lab[:, :, 1:] = img_lab[:, :, 1:] * 255 - 128 #DENORMALIZE
    img_rgb = lab2rgb(img_lab.astype(np.float64)) 

    return img_rgb
