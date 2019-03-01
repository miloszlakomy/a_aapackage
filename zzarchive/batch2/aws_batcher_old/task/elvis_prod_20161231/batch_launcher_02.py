# -*- coding: utf-8 -*-
import os, sys
DIRCWD=  'D:/_devs/Python01/project27/' if sys.platform.find('win')> -1   else  '/home/ubuntu/notebook/' if os.environ['HOME'].find('ubuntu')>-1 else '/media/sf_project27/'
os.chdir(DIRCWD); sys.path.append(DIRCWD+'/aapackage');  sys.path.append(DIRCWD+'/linux/aapackage')
print('Directory Folder:'+str(DIRCWD))
import util, numpy as np
execfile( DIRCWD + '/aapackage/allmodule.py')
#########################################################################################################
import subprocess
IPYTHON_PATH='D:/_devs/Python01/Anaconda27/Scripts/ipython' if sys.platform.find('win') > -1   else  '/home/ubuntu/anaconda2/bin/ipython' if os.environ['HOME'].find('ubuntu') > -1 else "/home/linux1/anaconda2/bin/ipython"
##### NO SPACE in ipython path ---> Error in Shell COMMAND


############## Compute Params  #########################################################################
DIRBATCH= DIRCWD + "/linux/batch/task/" + "elvis_prod_20161228/"
try :
  fromfile1= sys.argv[0]
  extract_folder= fromfile1.split('/')[-2]            #  print 'Task Folder', task_folder
  DIRBATCH= DIRCWD + "/linux/batch/task/" + extract_folder + '/'
except : pass

input_param_file= DIRBATCH+'input_params_all.pkl'

##### Get Config for EC2  ###########
execfile( DIRBATCH+'/ec2_config.py')
# NCPU=  2


print  'Nb CPU: ', NCPU,  'Directory Batch:', DIRBATCH, '\n'


'''
c4.4xlarge 	16 CPU  $0.1293 - 0.20, Stable
c4.8xlarge 	36 CPI  $0.30 - 0.50, unstable

Combinaison :
4**6: 4096,    5**6: 15000,   7**5; 16800,  8**5: 32765

'''




##################################################################################################
################# Split task across cpu ##########################################################
# NCPU=  10
nhour= 3.0
input_param= util.py_load_obj( input_param_file  ,isabsolutpath=1)
ntask= input_param.shape[0]; del input_param

ncpu_time=  NCPU * nhour
nsplit=     NCPU
splitsize = int(np.round(ntask / NCPU, 0))
print '\n ntask:', ntask, 'nsplit:', nsplit, 'splitsize:', splitsize, '\n\n'

#Create task_id list : File of Input,  jstart, jend
task_id_list=[(input_param_file, splitsize * i,  splitsize * (i+1)) for  i in xrange(0, nsplit-1)    ]
task_id_list.append((input_param_file, splitsize*(nsplit-1), ntask) )


#Create the NCPU process :
script_list= [ (DIRBATCH + 'pygmo_batch_generic.py', '0,0')  for i in xrange(0, nsplit) ]




##############  Launch the sub-process task on each split(=cpu)   ##################################
proc_list=[]
for ii, task_id in enumerate(task_id_list) :
  file1, j0, j1=     task_id
  filescript, args1= script_list[ii]
  print 'CPU_ID:'+str(ii), (j0,j1), filescript

  #Launch with istart, iend of each task
  cmd_list= [IPYTHON_PATH, filescript, str(( task_id , args1))]

  proc= subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  proc_list.append( proc)

####################################################################################################







##################################################################################################
#   proc= subprocess.Popen(['/home/ubuntu/anaconda2/bin/ipython',  '/home/ubuntu/notebook/linux/batch/task/elvis_prod_20161220/pygmo_batch_02.py'])

'''   Test of small task list
task_id_list=[]
task_id_list.append(  ('D:/_devs/Python01/project27//linux/batch/task/elvis_prod_20161220/input_params_all.pkl', 36,  48L) )
script_list= [ (DIRBATCH_local + 'pygmo_batch_generic.py', '0,0')  ]

'''


'''  Manual Test in Terminal

ipython D:/_devs/Python01/project27//linux/batch/task/elvis_prod_20161220/pygmo_batch_generic.py   "(('D:/_devs/Python01/project27//linux/batch/task/elvis_prod_20161220/input_params_all.pkl', 36, 48L), '0,0')"

##linux  1 Task Launcher
ipython /media/sf_project27/linux/batch/task/elvis_prod_20161220/pygmo_batch_generic.py   "(('/media/sf_project27/linux/batch/task/elvis_prod_20161220/input_params_all.pkl', 36, 48L), '0,0')"


###Linux Full Batch Launcher
ipython /media/sf_project27/linux/batch/task/elvis_prod_20161228/batch_launcher_02.py


"(('D:/_devs/Python01/project27//linux/batch/task/elvis_prod_20161220/input_params_all.pkl', 36, 48L), '0,0')"

'''



'''
############## Bacth Session 1 ######################################################
DIRBATCH_local= DIRCWD+"/linux/batch/task/elvis_prod_20161220/"
print DIRBATCH_local

script_list= [
(DIRBATCH_local + 'pygmo_batch_02.py', '0,0'),
(DIRBATCH_local + 'pygmo_batch_02.py', '0,0'),
(DIRBATCH_local + 'pygmo_batch_02.py', '0,0'),

]

print '\n', IPYTHON_PATH, '\n', DIRBATCH_local

proc_list= []
for ii, scriptdata in   enumerate(script_list) :
  filescript, args1= scriptdata
  print(ii, filescript)
  cmd_list= [IPYTHON_PATH, filescript, args1]
  proc= subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  proc_list.append( proc)

####################################################################################
'''




'''
#  Kill on exit
import atexit
@atexit.register
def kill_subprocesses():
    for proc in proc_list:
        proc.kill()
        
        
# kill_subprocesses()
'''


'''  Manual Check

proc0= proc_list[0]
stdout, stderr = proc0.communicate()
print("Console Msg: \n"+ str(stdout))  #,"utf-8"))  
print("\nConsole Error: \n"+ str(stderr) ,  'Error Code:'+str(proc0.returncode))


filescript= DIRCWD+"/linux/pygmo_batch_test.py"
cmd_list= [IPYTHON_PATH, filescript]
proc0= subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


'''


