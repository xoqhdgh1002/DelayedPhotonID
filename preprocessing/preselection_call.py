import os, sys
import subprocess
cwd = os.getcwd()
print("Current dir: {}".format(cwd))
source_file = 'getcmssw.sh'
with open(source_file, "w") as sf:
    sf.write('#!/bin/bash\n')
    sf.write('cd /storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/\n')
    sf.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    sf.write('eval `scram runtime -sh`\n')
    sf.write('cd {}\n'.format(cwd))
    sf.write('python /storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/preselection.py {}'.format(sys.argv[1])) 
os.chmod(source_file, 0775)
subprocess.call('./{}'.format(source_file), shell=True)

