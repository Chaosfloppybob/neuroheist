import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
from x import BrainDataset
from config import *
from backend.old_model import UNet
from split_data import create_split

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_samples, val_samples = create_split()
train_dataset = BrainDataset(train_samples, target_shape=(16, 128, 128))
val_dataset = BrainDataset(val_samples, target_shape=(16, 128, 128))
train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, num_workers=2, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False, num_workers=2, pin_memory=True)
model = UNet(in_channels=1, num_classes=4)
optimizer = optim
model = model.to(device)
num_epochs = 50

for epoch in range(num_epochs):
    model.train()
    running_train_loss = 0.0
    for images, masks in train_loader:
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)
        predictions = model(images)






    model.eval()
    running_val_loss = 0.0