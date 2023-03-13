import os, sys
from glob import glob
import subprocess

if not os.path.isdir('submit'):
    os.mkdir('submit')
if not os.path.isdir('log'):
    os.mkdir('log')

curr_dir = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/deployment/'
skim_list = ['DoubleEG', 'GMSB'] #, 'DiPhoton', 'GJets', 'QCD']
skim_file = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/deployment/inference_call.sh'
in_dir = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/skim_analyzer_output_baselineCut_noTrigger/'

# Collect the list of txt files to skim
#process_list = []
#for this_file in glob(in_dir+'/*.root'):
#    for sample in skim_list:
#        if sample in this_file: process_list.append(this_file)

process_list = glob(in_dir+'/*.root')

# For each item in the list, submit a condor job
for sample in process_list:
    print("Processing {}".format(sample))
    condorlog_name = sample.split('/')[-1].replace('-','_').replace('root','condorlog')
    log_name = sample.split('/')[-1].replace('-','_').replace('root','log')
    err_name = sample.split('/')[-1].replace('-','_').replace('root','err')
    jdl_name = sample.split('/')[-1].replace('-','_').replace('root','jdl')
    if os.path.isfile(curr_dir+'/submit/'+jdl_name):
        os.remove(curr_dir+'/submit/'+jdl_name)
    if os.path.isfile(curr_dir+'/log/'+log_name):
        os.remove(curr_dir+'/log/'+log_name)
        os.remove(curr_dir+'/log/'+err_name)

    with open(curr_dir+"/submit/"+jdl_name, "w") as condor_file:
        script = "Universe = vanilla\n"
        script += "Executable = {}\n".format(skim_file)
        script += "Arguments = {}\n".format(sample)
        script += "Log = {}/log/{}\n".format(curr_dir, condorlog_name)
        script += "Output = {}/log/{}\n".format(curr_dir, log_name)
        script += "Error = {}/log/{}\n".format(curr_dir, err_name)
        script += "should_transfer_files = YES\n"
        script += "RequestMemory = 2000\n"
        script += "RequestCpus = 1\n"
        script += "x509userproxy = /storage/user/qnguyen/my_proxy\n"
        script += "+RunAsOwner = True\n"
        script += "+InteractiveUser = true\n"
        script += "+SingularityImage = \"/storage/user/qnguyen/gpuservers/singularity/images/cutting_edge_torch1.4.simg\"\n"
        script += "+SingularityBindCVMFS = False\n"
        script += "when_to_transfer_output = ON_EXIT\n"
        script += "+JobBatchName = \"{}\"\n".format(jdl_name)
        script += "Queue 1\n"
        condor_file.write(script)

    subprocess.call("condor_submit {}/submit/{}".format(curr_dir, jdl_name), shell=True)