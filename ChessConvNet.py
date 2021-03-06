import torch
import torch.nn as nn

class ChessConvNet(nn.Module):
    def __init__(self, num_classes):
        super(ChessConvNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2), # 1, 64
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),  #64, 128
            nn.BatchNorm2d(32),  #128
            nn.Tanh(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),  #128, 128
            nn.BatchNorm2d(64),
            nn.Tanh(),
            nn.MaxPool2d(kernel_size=1, stride=1))
        self.fc = nn.Linear(28 * 2 * 64, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out