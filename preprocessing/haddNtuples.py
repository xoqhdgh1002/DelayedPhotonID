import os, sys
import shutil
import subprocess
with open(sys.argv[1], "r") as infile:
    listfile = infile.readlines()
# Create a set of unique directories
setfile = set()
for infile in listfile:
    dirfile = '/'.join(infile.split('/')[:-1])
    setfile.add(dirfile)
print(setfile)

print("hadding files from {}...".format(sys.argv[1]))
outfile = sys.argv[1].split('/')[-1].replace('txt','root').replace('-','_')
print("Output file: {}".format(outfile))

cwd = os.getcwd()
print("Current directory: {}".format(cwd))

source_file = outfile.replace('.root','.sh')
with open(source_file, "w") as sf:
    sf.write('#!/bin/bash\n')
    sf.write('cd /storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/\n')
    sf.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    sf.write('eval `scram runtime -sh`\n')
    sf.write('cd {}\n'.format(cwd))
    sf.write('hadd -k -f {}'.format(outfile))
    for indir in setfile:
        sf.write(' {}/*'.format(indir))
os.chmod(source_file, 0775)
print("Written source cmd to {}".format(source_file))
subprocess.call('./{}'.format(source_file), shell=True)
destination = '/storage/user/qnguyen/DelayedPhoton/CMSSW_10_6_6/src/DelayedPhotonID/preprocessing/ntuplizer_hadd_output/'+outfile
dest = shutil.move(outfile, destination)
print("Moved output file to {}".format(destination))
