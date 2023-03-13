import uproot as ur
import ROOT as rt
import pandas as pd
import numpy as np
from glob import glob
import os, sys
import re

###################################
# Select which photon to process
if len(sys.argv) < 1:
    pho = 1 
    print("Processing leading photon")
else: 
    pho = sys.argv[1]
    print("Processing photon {}".format(pho))
pho = int(pho)
if pho not in [1, 2]:
    print("Process photon must be either 1 or 2")
    sys.exit()
###################################
QCD_factor = 2.5 #skim_analyzer_output_reproduce_cutBothPho_CR
indir1 = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_analyzer_output_reproduce_minimalCut_cutBothPho/'
indir2 = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_analyzer_output_triggerEffCuts_noDistanceCut/'

if pho == 1:
    indir = indir1
else:
    indir = indir2

outdir = indir + '/csv_out/'

if not os.path.isdir(outdir):
    print("Making directory {}".format(outdir))
    os.mkdir(outdir)

convert_list = ['GMSB', 'DiPhoton', 'GJet', 'QCD', 'W', 'Z', 'tt', 'T']
event_branches = ['weight', 'pileupWeight', 'triggerEffSFWeight', 'photonEffSF']
decay_branches = ['R1', 'pho1_genVtxZ']
pho1_branches = ['pho1ecalPFClusterIso', 'pho1hcalPFClusterIso',
                'pho1trkSumPtHollowConeDR03', 'pho1R9', 'pho1SigmaIetaIeta', 'pho1Smajor', 'pho1Sminor',
                'pho1passIsoLoose_comboIso', 'pho1passIsoMedium_comboIso', 'pho1passIsoTight_comboIso',
                'pho1passEleVeto', 'pho1Sminor', 'pho1passSigmaIetaIetaTight', 'pho1passHoverETight', 
                'pho1passSmajorTight', 'pho1Pt']
pho2_branches = ['pho2ecalPFClusterIso', 'pho2hcalPFClusterIso',
                'pho2trkSumPtHollowConeDR03', 'pho2R9', 'pho2SigmaIetaIeta', 'pho2Smajor', 'pho2Sminor',
                'pho2passIsoLoose_comboIso', 'pho2passIsoMedium_comboIso', 'pho2passIsoTight_comboIso']

lumi_2016 = 35922.0
lumi_2017 = 41530.0
lumi = lumi_2016

def getXS(sample):
    """Get cross section for background MC"""
    dat_file = "/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/data/all_bkg_back.list"
    with open(dat_file, "r") as xsfile:
        allxs = xsfile.readlines()
        for xs in allxs[1:]:
            if xs.split(' ')[0] in sample:
                xs_val = xs.strip().split(' ')[-1].replace('\n','')
                try:
                    return float(xs_val)
                except ValueError as e:
                    print(e)
                    print("\nSample with problem: {}\nLine to process: {}\nString to convert: ({})".format(sample, xs, xs_val))
                    sys.exit()
    print("[WARNING] {} cross section not found in {}".format(sample, dat_file))
    return 0

def extract_num(string):
    sample_num = list(map(int, re.findall(r'\d+', string.split('/')[-1])))
    if len(sample_num) > 1:
        sample_lambda, sample_ctau = sample_num[0], sample_num[1]
        if sample_ctau == 0:
            if "0_001cm" in string:
                sample_ctau = 0.001
            elif "0_01cm" in string:
                sample_ctau = 0.01
            elif "0_1cm" in string:
                sample_ctau = 0.1

        return sample_lambda, sample_ctau
    else:
        print("Can't extract number from {}".format(string))
        return 0, 0

def getSignalXS(sample):
    """Get cross section x BR for signal MC"""
    sample_lambda, sample_ctau = extract_num(sample)
    
    dat_file = "/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/data/XsecBR.dat"
    with open(dat_file, "r") as xsfile:
        allxs = xsfile.readlines()
        for xs in allxs[1:]:
            this_lambda, this_ctau = extract_num(xs)
            if sample_lambda == this_lambda and sample_ctau == this_ctau:
                return float(xs.split(' ')[4])
    print("[WARNING] {} cross section not found in {}".format(sample, dat_file))
    return 0

# Collect the list of root files to convert
process_list = []
for this_file in glob(indir+'/*.root'):
    for sample in convert_list:
        if 'DelayedPhoton_'+sample in this_file: process_list.append(this_file)
        

# For each item in the list, do the conversion
for sample in process_list:
    out_file = outdir + sample.split('/')[-1].replace('root', 'csv')
    intree = ur.rootio.open(sample).get("DelayedPhoton")
    
    # Load different branches
    inevent = intree.pandas.df(branches=event_branches)
    inpho1 = intree.pandas.df(branches=pho1_branches)
    inpho2 = intree.pandas.df(branches=pho2_branches)
    
    # Merge pho1 and pho2
#    inpho1.columns = inpho1.columns.str.replace("pho1","pho")
#    inpho2.columns = inpho2.columns.str.replace("pho2","pho")
    inpho1e = pd.concat([inevent, inpho1], axis=1, sort=False)
    inpho2e = pd.concat([inevent, inpho2], axis=1, sort=False)
    #inpho = pd.concat([inpho1e, inpho2e], ignore_index=True)
    if pho == 1:
        inpho = inpho1e
    else:
        inpho = inpho2e

    # Get the cross section divided by sum weights
    if 'GMSB' not in sample: 
        xsec = getXS(sample)
        if "QCD" in sample:
            xsec *= QCD_factor
        inpho['R1'] = 1.
        inpho['pho1_genVtxZ'] = 1.
    else:
        indecay = intree.pandas.df(branches=decay_branches)
        inpho = pd.concat([inpho, indecay], axis=1, sort=False)
        xsec = getSignalXS(sample)
        sample_lambda, sample_ctau = extract_num(sample.split('/')[-1])
        if int(sample_lambda) < 200: continue # Don't care about samples already excluded
        #if float(sample_ctau) < 150: continue # Don't care about low ctau, just for testing
        if pho == 2:
            # For diphoton category, focus on low ctau
            if float(sample_ctau) > 201: continue
        inpho["lambda"] = int(sample_lambda)
        inpho["ctau"] = float(sample_ctau)
    
    infile = rt.TFile.Open(sample, "READ")
    sw_hist = infile.Get("SumWeights")
    sumWeights = sw_hist.Integral()
    infile.Close()
    xsecOverSum = xsec/sumWeights
    if 'GMSB' not in sample:
        inpho['xsecOverSum'] = xsecOverSum
    else:
        # For signal, need to make sure the weight across all surviving samples are the same. Please run signalCount.py to obtain the sum of all suviving samples
        leadSum = 26359 # obtained from signalCount.py
        subleadSum = 1872714
        if pho == 1:
            ls = leadSum
        else:
            ls = subleadSum
        survived = len(inpho) 
        # no scale for now
        inpho['xsecOverSum'] = 1 #float(ls/survived)

    inpho.to_csv(out_file, index=False)
    print("Saved output to {}".format(out_file))
