import torch.nn as nn
import torch 
import torch.nn.functional as F

### Define classifier model
net = nn.Sequential(nn.Linear(7, 300),
        nn.ReLU(),
        nn.Linear(300, 200),
        nn.Dropout(0.5),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(200, 20),
        nn.Dropout(0.7),
        nn.ReLU(),
        nn.Linear(20, 1),
        nn.Sigmoid())

class Classifier(nn.Module):
    def __init__(self, in_dim=7, dropout=0.5):
        super(Classifier, self).__init__()
        self.dropout = nn.Dropout(p=dropout, inplace=True)
        self.lin1 = nn.Linear(in_dim, 30)
        self.lin2 = nn.Linear(30, 200)
        self.lin3 = nn.Linear(200, 20)
        self.lin4 = nn.Linear(20, 1)
        self.out = nn.Sigmoid()
        self.penultimate_layer = None

    def penultimate(self, x):
        self.penultimate_layer = self.lin1(x)
        return self.penultimate_layer

    def forward(self, x):
        x = F.relu(self.penultimate(x))
        x = self.dropout(x)
        x = F.relu(self.lin2(x))
        x = self.dropout(x)
        x = self.lin3(x)
        x = self.dropout(x)
        x = self.out(self.lin4(x))
        return x

class Adversarial(nn.Module):
    def __init__(self, in_dim=30, dropout=0.5):
        super(Adversarial, self).__init__()
        self.dropout = nn.Dropout(p=dropout, inplace=True)
        self.lin1 = nn.Linear(in_dim, 20)
        self.lin2 = nn.Linear(20, 10)
        self.lin3 = nn.Linear(10, 1)
        #self.out = nn.Sigmoid()

    def forward(self, x):
        x = F.relu(self.lin1(x))
        x = self.dropout(x)
        x = F.relu(self.lin2(x))
        x = self.dropout(x)
        x = self.lin3(x)
        return x

