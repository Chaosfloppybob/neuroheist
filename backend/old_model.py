import torch
import torch.nn as nn

class DoubleConv3D(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv3D, self).__init__()
        self.conv1 = nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1)
        self.norm1 = nn.BatchNorm3d(out_channels)
        self.conv2 = nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1)
        self.norm2 = nn.BatchNorm3d(out_channels)
        self.relu = nn.ReLU(inplace=True)
    def forward(self, x):
        return self.relu(self.norm2(self.conv2(self.relu(self.norm1(self.conv1(x))))))

class UNet(nn.Module):
    def __init__(self, in_channels = 4, num_classes = 4):
        super(UNet, self).__init__()
        self.encoder1 = DoubleConv3D(in_channels, 32)
        self.pool1 = nn.MaxPool3d(kernel_size=2, stride=2)
        self.encoder2 = DoubleConv3D(32, 64)
        self.pool2 = nn.MaxPool3d(kernel_size=2, stride=2)
        self.encoder3 = DoubleConv3D(64, 128)
        self.pool3 = nn.MaxPool3d(kernel_size=2, stride=2)
        self.bottleneck = DoubleConv3D(128, 256)
        self.up3 = nn.ConvTranspose3d(256, 128, kernel_size=2, stride=2)
        self.decoder3 = DoubleConv3D(256, 128)
        self.up2 = nn.ConvTranspose3d(128, 64, kernel_size=2, stride=2)
        self.decoder2 = DoubleConv3D(128, 64)
        self.up1 = nn.ConvTranspose3d(64, 32, kernel_size=2, stride=2)
        self.decoder1 = DoubleConv3D(64, 32)
        self.output = nn.Conv3d(32, num_classes, kernel_size=1)
    def forward(self, x):
        e3 = self.up3(self.bottleneck(self.pool3(self.encoder3(self.pool2(self.encoder2(self.pool1(self.encoder1(x))))))))
        e3 = torch.cat([e3, self.encoder3(self.pool2(self.encoder2(self.pool1(self.encoder1(x)))))], dim=1)
        e2 = self.up2(self.decoder3(e3))
        e2 = torch.cat([e2, self.encoder2(self.pool1(self.encoder1(x)))], dim = 1)
        e1 = self.up1(self.decoder2(e2))
        e1 = torch.cat([e1, self.encoder1(x)], dim = 1)
        output = self.output(self.decoder1(e1))
        return output