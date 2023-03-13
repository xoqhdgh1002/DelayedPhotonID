import os, sys
os.environ['CUDA_VISIBLE_DEVICES'] = '4'
sys.path.append('/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/models/')
import torch
from model import net # Classifier
import pandas as pd
import numpy as np
import uproot
import copy
import ROOT as rt
import root_numpy
import array

model_path1 = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_minimalCut_wPt/models/state_dict_highCtau_best.pth'
model_path2 = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_sub/models/state_dict_sub.pth'

mean1 = np.load('/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_minimalCut_wPt/mean.npy')
std1 = np.load('//storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_minimalCut_wPt//std.npy')
mean2 = np.load('/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_sub/mean.npy')
std2 = np.load('/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/training_sub/std.npy')

outdir = './'
#outdir = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/deployment/output_baselineCut_noTrigger/'

random_seed = 42

if len(sys.argv) < 2:
    print("ERROR: Please provide input dataset")
    sys.exit()

infileName = sys.argv[1]
if not os.path.isfile(infileName):
    print("ERROR: File {} does not exist".format(infileName))
    sys.exit()

if not os.path.isdir(outdir):
    print("Creating {}".format(outdir))
    os.mkdir(outdir)

outfileName = outdir+'/'+infileName.split('/')[-1]
print("Will save output to {}".format(outfileName))

### Check CUDA availability
isCUDA = torch.cuda.is_available()

### Create 2 instances for 2 photons
net1 = copy.deepcopy(net)
#net1 = Classifier() #copy.deepcopy(net)
#net2 = copy.deepcopy(net)

# Load the trained model
if isCUDA:
    net1.load_state_dict(torch.load(model_path1))
 #   net2.load_state_dict(torch.load(model_path2))
else:
    net1.load_state_dict(torch.load(model_path1, map_location=torch.device('cpu')))
  #  net2.load_state_dict(torch.load(model_path2, map_location=torch.device('cpu')))

net1.eval()
#net2.eval()

# Move back to CPU for faster inference (and also we have no GPU on supercluster)
net1.cpu()
#net2.cpu()

### Game on!
pho_branches = ['pho{}ecalPFClusterIso', 'pho{}hcalPFClusterIso', 
                'pho{}trkSumPtHollowConeDR03', 'pho{}R9', 
                'pho{}SigmaIetaIeta', 'pho{}Smajor', 'pho{}Sminor', 'pho{}Pt']

### Create output root file
appendFile = rt.TFile.Open(infileName, "READ")
outfile = rt.TFile.Open(outfileName, "RECREATE")
inTree = appendFile.Get("DelayedPhoton")

outTree = inTree.CloneTree(0)

### Input variable construction
processLine = {}
for pho in [1]:
    processLine[pho] = 'struct MyStruct_inpho{}{{\n'.format(pho)
    for var in pho_branches:
        varfill = var.format(pho)
        processLine[pho] += "\tfloat {};\n".format(varfill)
    processLine[pho] += '};'
    rt.gROOT.ProcessLine(processLine[pho])

from ROOT import MyStruct_inpho1#, MyStruct_inpho2

in_pho1 = MyStruct_inpho1()
#in_pho2 = MyStruct_inpho2()

for var in pho_branches:
    varfill = var.format(1)
    inTree.SetBranchAddress(varfill, rt.AddressOf(in_pho1, varfill))
#    varfill = var.format(2)
#    inTree.SetBranchAddress(varfill, rt.AddressOf(in_pho2, varfill))

### Output struct
rt.gROOT.ProcessLine("struct MyStruct_pho1{float pho1DNN;};")
#rt.gROOT.ProcessLine("struct MyStruct_pho2{float pho2DNN;};")

from ROOT import MyStruct_pho1
#from ROOT import MyStruct_pho2

# Create new branches
s_pho1 = MyStruct_pho1()
#s_pho2 = MyStruct_pho2()

outTree.Branch('pho1DNN', rt.AddressOf(s_pho1, 'pho1DNN'), 'pho1DNN/F')
#outTree.Branch('pho2DNN', rt.AddressOf(s_pho2, 'pho2DNN'), 'pho2DNN/F')

with torch.no_grad():
    for i in range(inTree.GetEntries()):
        inTree.GetEntry(i)
        if i % 10000 == 0:
            print("Processing event {}/{}".format(i, inTree.GetEntries()))
        
        DNNinput1 = np.asarray([in_pho1.pho1ecalPFClusterIso/in_pho1.pho1Pt,
                                in_pho1.pho1hcalPFClusterIso/in_pho1.pho1Pt,
                                in_pho1.pho1trkSumPtHollowConeDR03/in_pho1.pho1Pt,
                                in_pho1.pho1R9,
                                in_pho1.pho1SigmaIetaIeta,
                                in_pho1.pho1Smajor,
                                in_pho1.pho1Sminor
                                ])

#        DNNinput2 = np.asarray([in_pho2.pho2ecalPFClusterIso,
#                                in_pho2.pho2hcalPFClusterIso,
#                                in_pho2.pho2trkSumPtHollowConeDR03,
#                                in_pho2.pho2R9,
#                                in_pho2.pho2SigmaIetaIeta,
#                                in_pho2.pho2Smajor,
#                                in_pho2.pho2Sminor])
        normed_inference_input1 = torch.from_numpy((DNNinput1 - mean1)/std1).float()
#        normed_inference_input2 = torch.from_numpy((DNNinput2 - mean2)/std2).float()
        score1 = net1(normed_inference_input1.view(1, -1)).data.numpy()
#        score2 = net2(normed_inference_input2.view(1, -1)).data.numpy()
        s_pho1.pho1DNN = score1
#        if np.isnan(score1):
#            print("NaN detected")
#            print("Input: {}".format(DNNinput1))
#            print("Normalized input: {}".format(normed_inference_input1.data.numpy()))

#        s_pho2.pho2DNN = score2
        outTree.Fill()
outTree.GetCurrentFile().Write()

# Clone the histograms 
keyList = appendFile.GetListOfKeys()
outfile.cd()
for key in keyList:
    className = key.GetClassName()
    fName = key.GetName()
    if className == "TH1F":
        appendFile.cd()
        histThis = appendFile.Get(fName)
        outfile.cd()
        histOut = histThis.Clone()
        histOut.Write()

outfile.Close()
appendFile.Close()
print("Written to {}".format(outfileName))
