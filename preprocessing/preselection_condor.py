import os, sys
from glob import glob
import subprocess

if not os.path.isdir('submit'):
    os.mkdir('submit')
if not os.path.isdir('log'):
    os.mkdir('log')

curr_dir = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/'
skim_list = ['GMSB', 'DiPhoton', 'GJets', 'QCD', 'tt', 'T', 'W', 'Z']
skim_file = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/preselection_call.py'
in_dir = '/mnt/hadoop/store/group/phys_susy/razor/Run2Analysis/DelayedPhotonAnalysis/2016/legacy/hadd/'

# Collect the list of txt files to skim
process_list = glob(in_dir+'/*.root')

# For each item in the list, submit a condor job
for sample in process_list:
    print("Processing {}".format(sample))
    condorlog_name = sample.split('/')[-1].replace('-','_').replace('root','condorlog')
    log_name = sample.split('/')[-1].replace('-','_').replace('root','log')
    err_name = sample.split('/')[-1].replace('-','_').replace('root','err')
    jdl_name = sample.split('/')[-1].replace('-','_').replace('root','jdl')
    batch_name = sample.split('/')[-1].split('_')[0]
    if os.path.isfile(curr_dir+'/submit/'+jdl_name):
        os.remove(curr_dir+'/submit/'+jdl_name)
    if os.path.isfile(curr_dir+'/log/'+log_name):
        os.remove(curr_dir+'/log/'+log_name)
        os.remove(curr_dir+'/log/'+err_name)

    with open(curr_dir+"/submit/"+jdl_name, "w") as condor_file:
        script = "Universe = vanilla\n"
        script += "Executable = /cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_6_6/external/slc7_amd64_gcc700/bin/python\n"
        script += "Arguments = {} {}\n".format(skim_file, sample)
        script += "Log = {}/log/{}\n".format(curr_dir, condorlog_name)
        script += "Output = {}/log/{}\n".format(curr_dir, log_name)
        script += "Error = {}/log/{}\n".format(curr_dir, err_name)
        script += "should_transfer_files = YES\n"
        script += "RequestMemory = 2000\n"
        script += "RequestCpus = 1\n"
        script += "x509userproxy = /storage/user/qnguyen/my_proxy\n"
        script += "+RunAsOwner = True\n"
        script += "+InteractiveUser = true\n"
        script += "+SingularityImage = \"/cvmfs/singularity.opensciencegrid.org/bbockelm/cms:rhel7\"\n"
        script += "+SingularityBindCVMFS = True\n"
        script += "when_to_transfer_output = ON_EXIT\n"
        script += "+JobBatchName = \"{}\"\n".format(batch_name)
        script += "Queue 1\n"
        condor_file.write(script)

    subprocess.call("condor_submit {}/submit/{}".format(curr_dir, jdl_name), shell=True)
