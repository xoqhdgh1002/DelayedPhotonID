import os, sys
import subprocess
import ROOT as rt

pho = 1

event_cut = 'n_Photons == 1'
njets_cut = '&& n_Jets > 2'
cr_cut = '&& abs(pho1ClusterTime_SmearToData) < 1.0 && MET < 100'
pho1_cut = ' && pho1Pt > 70 && abs(pho1Eta)<1.4442 && pho1passEleVeto && abs(pho1HoverE) < 0.08 && pho1R9 > 0.85 && abs(pho1SigmaIetaIeta) < 0.024' #&& abs(pho1ecalPFClusterIso) < 7.5 && abs(pho1hcalPFClusterIso) < 5.0 && abs(pho1trkSumPtHollowConeDR03) < 7.5 && pho1passEleVeto'
pho2_cut = '&& pho2SigmaIetaIeta < 0.03 \
            && pho2HoverE < 0.1 \
            && pho2ecalPFClusterIso < 30.0 \
            && pho2sumNeutralHadronEt < 30.0 \
            && pho2trkSumPtHollowConeDR03 < 30.0'
met_cut = " && Flag_HBHENoiseFilter == 1 && Flag_HBHEIsoNoiseFilter ==1 && Flag_goodVertices == 1 && Flag_eeBadScFilter == 1 && Flag_EcalDeadCellTriggerPrimitiveFilter == 1 && Flag_CSCTightHaloFilter == 1  && Flag_badMuonFilter == 1 && Flag_badGlobalMuonFilter == 0 && Flag_duplicateMuonFilter == 0 " 
outDir = "/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_legacy2016_singlephoton/"
signal_cut = " && abs(pho1_genVtxZ) > 20 && R1 > 20 "
infile = sys.argv[1]

if "QCD_HT" in infile or "GJets_HT" in infile: 
    # Don't care about these samples
    sys.exit()


if pho == 1: 
    pho_cut = pho1_cut
elif pho == 2:
    pho_cut = pho2_cut
else:
    pho_cut = pho1_cut + pho2_cut

if not os.path.isdir(outDir):
    print("Making {}".format(outDir))
    os.mkdir(outDir)

thisFile = rt.TFile.Open(infile, "READ")
keyList = thisFile.GetListOfKeys()
if "DelayedPhoton" not in infile.split('/')[-1]:
    outFileName = outDir + "DelayedPhoton_"+infile.split('/')[-1]
else:
    outFileName = outDir + infile.split('/')[-1]
outputFile = rt.TFile(outFileName, "RECREATE")
outputFile.cd()

cutSkim = event_cut + met_cut + pho_cut 
#if "QCD" not in infile: cutSkim += njets_cut 
#if "GMSB" in infile: cutSkim += signal_cut
#if "DoubleEG" in infile: cutSkim += cr_cut

for key in keyList:
    className = key.GetClassName()
    fName = key.GetName()
    print("Reading {}: {} {}".format(key, className, fName))
    if className == "TTree":
        thisFile.cd()
        inputTree = thisFile.Get(fName)
        print("Input events: {}".format(inputTree.GetEntries()))
        outputFile.cd()
        outputTree = inputTree.CopyTree(cutSkim)
        print("Output events: {}".format(outputTree.GetEntries()))
        outputTree.Write()
    elif className == "TH1F":
        thisFile.cd()
        thisHist = thisFile.Get(fName)
        outputFile.cd()
        histOut = thisHist.Clone()
        histOut.Write()
print("Output written to {}".format(outFileName))
