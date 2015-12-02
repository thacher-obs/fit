"""
Created on Mon Nov 16 21:49:05 2015

@author: douglas
"""

import ebsim as ebs
import run_ebsim as reb
import ebsim_results as ebres
import glob
import pdb
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def doug_test(network='doug'):
    bests = np.array(load_bestparams(network))
    trues = load_truevalues(network)
    initials = load_initialparams(network)
    nruns = len(bests)
    
    
    #standard error: (measured-real)/(1/2 * onesigma)
    #confidence interval: (1/2 * onesigma)/(real value)
    
    plt.figure()
    plt.ion()
    ival = 0 #m1
    bins_dict = {}
    for nrun in range(nruns):
        ste = (bests[nrun][ival][1] - trues[nrun][ival])/(.5*bests[nrun][ival][3])
        CI = (.5*bests[nrun][ival][3])/(trues[nrun][ival]) * 100
        t = initials[nrun][1]
        if t in bins_dict.keys():
            bins_dict[t].append(CI)
        else:
            bins_dict[t] = [CI]
    for val in bins_dict.keys():
        mean = np.average(bins_dict[val])
        std = np.std(bins_dict[val])
        plt.plot([val]*len(bins_dict[val]), bins_dict[val], 'o')
        #plt.errorbar(v al, mean, yerr=std,fmt='o')
       # plt.plot()

    plt.xlabel('Integration Time')
    plt.ylabel('M1 Confidence Interval (%)')
    if network=='bellerophon':
        plt.savefig('/home/administrator/Desktop/dougtest.png')    
    
    
def load_bestparams(network='bellerophon'):
    """Loads the contents of all bestparams.txt's""" 
    path = reb.get_path(network)
    shorts = glob.glob(path + 'short/*/bestparams.txt')
    longs = glob.glob(path + 'long/*/bestparams.txt')
    
    bests = {'short':np.ndarray(324, pd.DataFrame),'long':np.ndarray(324, pd.DataFrame)}
    for bestparams in shorts:
        run = int(bestparams.split('/')[-2])
        vals = [float(val) for val in open(bestparams).readline().strip().replace("  "," ").split(" ")[1:]]
        vals = np.reshape(vals, [5,4])
        bests['short'][run] = pd.DataFrame(vals,index=['M1', 'M2', 'R1', 'R2', 'E'], columns=['Val', 'Med', 'Mode', 'Onesig'])
        
    for bestparams in longs:
        run = int(bestparams.split('/')[-2])
        vals = [float(val) for val in open(bestparams).readline().strip().replace("  "," ").split(" ")[1:]]
        vals = np.reshape(vals, [5,4])
        bests['long'][run] = pd.DataFrame(vals,index=['M1', 'M2', 'R1', 'R2', 'E'], columns=['Val', 'Med', 'Mode', 'Onesig'])
    
    
    #bests['short'].sort_index()
    #bests['long'].sort_index()
    #output shape: {short long} x runs x [Val Med Mode Onesig] x [M1 M2 R1 R2 E] 
    return bests

def load_truevalues(network='bellerophon'):
    """loads the contents of all ebpar.p's into an array"""
    path = reb.get_path(network)
    filenames = glob.glob(path + 'long/*/') #long and short trues identical
    trues = []
    runs = []
    for name in filenames:
        runs.append(int(name.split('/')[-2]))
        params = pickle.load( open( name+'ebpar.p', 'rb' ) )
        trues.append([params['Mstar1'],params['Mstar2'],params['Rstar1'],params['Rstar2'],np.sqrt(params['ecosw']**2 + params['esinw']**2)])
    
   
    #shape: runs x [m1,m2,r1,r2,e]
    return pd.DataFrame(trues, columns=['m1','m2','r1','r2','e'], index=runs).sort_index()

def load_initialparams(network='bellerophon'):
    """loads the contents of all initialparams.txt's into an array"""
    path = reb.get_path(network)
    filenames = glob.glob(path + 'long/*/initialparams.txt') #initialparams identical for longs and shorts
    initials = []
    runs = []
    for name in filenames:
        runs.append(int(name.split('/')[-2]))
        initials.append([float(a.strip()) for a in open(name).readlines()])
    
    #shape: runs x [period, photnoise, RVsamples, Rratio, impact]
    return pd.DataFrame(initials , columns=['period','photnoise','rvsamples','rratio','impact'], index=runs).sort_index()
