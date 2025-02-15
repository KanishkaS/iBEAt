""" 
@author: Joao Periquito 
iBEAt CLUSTER MAIN Scrpit
2022
Download XNAT dataset -> Name Standardization -> Execute MDR    -> Custom Moddeling (DCE, T2*, DCE)  -> T1 & T2 modelling with parallelization (done in the main)
    XNAT_cluster.py   ->  RENAME_Cluster.py   -> MDR_Cluster.py -> MODELLING_cluster.py
(T1 & T2 modelling are done in the main due to parallelization requirements)

TO RUN THE SCRIPT YOU USE: python main_cluster.py --num n (WHERE n is an integer with the value of the XNAT dataset)
"""

# To develop the application
# --------------------------
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

import os
import numpy as np

from tqdm import tqdm
import multiprocessing

import time
import datetime
from dbdicom import Folder
import argparse

import XNAT_cluster as xnat
import RENAME_cluster as rename
import MDR_cluster as mdr
import MODELLING_cluster as modelling
import T1T2_fw_modelling_cluster as T1T2_modelling

if __name__ == '__main__':

    #################### INPUT ######################
    username = "md1jdsp"
    password = "K_9X_Vuh3h"
    path = "//mnt//fastdata//md1jdsp//" + username #CLUSTER PATH TO SAVE DATA, ADD YOUR LOCAL PATH IF YOU WANT TO RUN IT LOCALLY
    #path = "C://Users//md1jdsp//Desktop//CLUSTER//CLUSTER_RESULTS"
    #################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--num',
                        dest='num',
                        help='Define the XNAT dataset',
                        type=int)

    args = parser.parse_args()

    dataset = [6,0,args.num]

    ################################################# EXAMPLE DATASET SELECTION #############################################################
    #DATASET CODE FOR LEEDS
    #  (FIRST NUMBER)                 (SECOND NUMBER)                                 (THIRD NUMBER - INNPUT from --num when you run the main script: python main_cluster.py --num n)
    #  2: BEAt-DKD-WP4-Bordeaux    (selected) BEAt-DKD-WP4-Leeds                 (selected) BEAt-DKD-WP4-Leeds -> (selected) Leeds_Patients
    #  3: BEAt-DKD-WP4-Exeter       ->0: Leeds_Patients                            0: Leeds_Patient_4128001
    #  4: BEAt-DKD-WP4-Turku          1: Leeds_volunteer_repeatability_study       1: Leeds_Patient_4128002
    #  5: BEAt-DKD-WP4-Bari           2: Leeds_Phantom_scans                       2: Leeds_Patient_4128004
    #->6: BEAt-DKD-WP4-Leeds          3: Leeds_RAVE_Reconstructions                       ..........
    #  7: BEAt-DKD-WP4-Sheffield      4: Leeds_setup_scans                      ->14: Leeds_Patient_4128015
    #########################################################################################################################################

    ExperimentName = xnat.main(username, password, path, dataset)
    # ExperimentName = "Leeds_Patient_4128003"
    pathScan = path + "//" + ExperimentName

    try: 
        UsedCores = int(len(os.sched_getaffinity(0)))
    except: 
        UsedCores = int(os.cpu_count())

    filename_log = pathScan + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH
    file = open(filename_log, 'a')
    file.write(str(datetime.datetime.now())[0:19] + ": Analysis of " + pathScan.split('//')[-1] +  " has started!")
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": CPU cores: " + str(UsedCores))
    file.close()

    start_time = time.time()
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming has started!")
    file.close()
    try:
        
        rename.main(pathScan)
        Folder(pathScan).scan()
        
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was completed --- %s seconds ---" % (int(time.time() - start_time)))
        file.close()
    except Exception as e:
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was NOT completed; error: "+str(e))
        file.close()

    start_time = time.time()
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR has started!")
    file.close()
    try:

        mdr.main(pathScan,filename_log)
        Folder(pathScan).scan()
        os.remove(pathScan + "//" + ExperimentName + ".csv")
        
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR was completed --- %s seconds ---" % (int(time.time() - start_time)))
        file.close()
    except Exception as e:
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR was NOT completed; error: "+str(e))
        file.close()

    start_time = time.time()
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling has started!")
    file.close()

    try:

        modelling.main(pathScan,filename_log)
        Folder(pathScan).scan()

        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
        file.close()
    except Exception as e:
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was NOT completed; error: "+str(e))
        file.close()

    # start_time = time.time()
    # file = open(filename_log, 'a')
    # file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling has started!")
    # file.close()

    # try:

    #     T1T2_modelling.main(pathScan,filename_log)
    #     Folder(pathScan).scan()

    #     file = open(filename_log, 'a')
    #     file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
    #     file.close()
    # except Exception as e:
    #     file = open(filename_log, 'a')
    #     file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling was NOT completed; error: "+str(e))
    #     file.close()

