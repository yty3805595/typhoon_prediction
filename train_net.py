'''
@Description: 
@Version: 1.0
@Author: Taoye Yin
@Date: 2019-08-20 22:06:56
@LastEditors: Taoye Yin
@LastEditTime: 2019-08-24 14:06:45
'''
from define_net import Net
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.init as init
import torch.optim as optim
import torch
import torchvision
import os
import torchvision.transforms as transforms
# from my_transform import transform

from my_image_folder import ImageFolder
import os,sys

def testset_loss(dataset,network):

    loader = torch.utils.data.DataLoader(dataset,batch_size=32,num_workers=2)

    all_loss = 0.0
    for i,data in enumerate(loader,0):

        inputs,labels = data
        inputs = Variable(inputs).to(device)

        outputs = network(inputs.to(device))  
        all_loss = all_loss + abs(labels[0]-outputs.data[0][0])

    return all_loss/i

if __name__ == '__main__':
	
    os.chdir(sys.path[0])
    path_ = os.path.abspath('.')
    transform = transforms.Compose([transforms.ToTensor(),
                            transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
    trainset = ImageFolder(path_+'/train_set/',transform)
    trainloader = torch.utils.data.DataLoader(trainset,batch_size=32,
                                              shuffle=True,num_workers=2)
    testset = ImageFolder(path_+'/test_set/',transform)
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print (device)
    net = Net().to(device)
    init.xavier_uniform_(net.conv1.weight.data,gain=1) #xaiver 初始化使每一层输出的方差尽量相等
    init.constant_(net.conv1.bias.data,0.1)
    init.xavier_uniform_(net.conv2.weight.data,gain=1)
    init.constant_(net.conv2.bias.data,0.1)
    #net.load_state_dict(torch.load(path_+'net_relu.pth')) 
    print (net)

    criterion = nn.L1Loss()

    optimizer = optim.Adam(net.parameters(),lr=0.003)

    for epoch in range(100): #

        running_loss = 0.0
        for i,data in enumerate(trainloader,0):

            inputs,labels = data
            inputs,labels = Variable(inputs).to(device),Variable(labels).to(device)

            optimizer.zero_grad()

            outputs = net(inputs.to(device))
            loss = criterion(outputs.squeeze(),labels.float())
            loss.backward()
            optimizer.step()

            running_loss += loss.data.item()
            if i%200 == 199:
                print('[%d, %5d] loss: %.3f' % (epoch+1,i+1,running_loss/200))
                running_loss = 0.0

        test_loss = testset_loss(testset,net)
        print('[%d] test loss: %.3f' % (epoch+1,test_loss))

    print('Finished Training')
    torch.save(net.state_dict(),path_+'/new_net_relu.pt')
