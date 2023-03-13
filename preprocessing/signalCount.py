import glob
import pandas as pd
import numpy as np
import re
from prettytable import PrettyTable
from collections import OrderedDict
indir = "/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_analyzer_output_reproduce_minimalCut_cutBothPho_decay20/csv_out_highCtau/"
indir2 = "/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_analyzer_output_triggerEffCuts_noDistanceCut/csv_out"

leadingSignal = list(sorted(glob.glob(indir+"/DelayedPhoton_GMSB*.csv")))
subLeadingSignal = list(sorted(glob.glob(indir2+"/GMSB*.csv")))

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

leadPho = OrderedDict()
secondPho = OrderedDict()
totalLead = 0
totalSecond = 0

for signal in leadingSignal:
    this_lambda, this_ctau = extract_num(signal.split('/')[-1])
    signalFile = pd.read_csv(signal)
    if (int(this_lambda), float(this_ctau)) in leadPho:
        leadPho[(int(this_lambda), float(this_ctau))] += len(signalFile) 
    else:
        leadPho[(int(this_lambda), float(this_ctau))] = len(signalFile)
    totalLead += len(signalFile)
for signal in subLeadingSignal:
    this_lambda, this_ctau = extract_num(signal.split('/')[-1])
    signalFile = pd.read_csv(signal)
    if (int(this_lambda), float(this_ctau)) in secondPho:
        secondPho[(int(this_lambda), float(this_ctau))] += len(signalFile) 
    else:
        secondPho[(int(this_lambda), float(this_ctau))] = len(signalFile)

    totalSecond += len(signalFile)

leadPhoTable = PrettyTable(["Lambda", "ctau", "Count", "Percentage (%)"])
for i, element in enumerate(leadPho):
    leadPhoTable.add_row([element[0], element[1], leadPho[element], "{:.2f}".format(float(leadPho[element])/totalLead * 100)])

leadPhoTable.sortby = "Count"
print(leadPhoTable)

secondPhoTable = PrettyTable(["Index", "Lambda", "ctau", "Count", "Percentage (%)"])
for i, element in enumerate(secondPho):
    secondPhoTable.add_row([i, element[0], element[1], secondPho[element], "{:.2f}".format(float(secondPho[element])/totalSecond * 100)])
secondPhoTable.sortby = "Count"

print(secondPhoTable)

print("Total number of leading photons: {}".format(totalLead))
print("Total number of subleading photons: {}".format(totalSecond))

