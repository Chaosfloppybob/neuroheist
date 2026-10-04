import torch
import os
from torch.utils.data import Dataset
import numpy as np


class BrainDataset(Dataset):

    def __init__(self, image_dir, mask_dir):

        self.image_dir = image_dir
        self.mask_dir = mask_dir

        self.image_files = sorted([
            f for f in os.listdir(image_dir)
            if f.endswith(".npy")
        ])

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, index):

        image_file = self.image_files[index]

        image_path = os.path.join(
            self.image_dir,
            image_file
        )

        mask_path = os.path.join(
            self.mask_dir,
            image_file
        )

        image = np.load(image_path)

        mask = np.load(mask_path)

        image = torch.from_numpy(image).float()

        mask = torch.from_numpy(mask).long()

        return image, mask