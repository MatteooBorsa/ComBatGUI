# -*- coding: utf-8 -*-


# Originally written by Nick Cullen
# Extended and currently maintained by JP Fortin
from __future__ import absolute_import, print_function
import pandas as pd
import numpy as np
import numpy.linalg as la
import math
import copy

def neuroCombat_estimate(dat,
           covars,
           batch_col,
           categorical_cols=None,
           continuous_cols=None,
           eb=True,
           parametric=True,
           mean_only=False,
           ref_batch=None):
    """
    Run ComBat to remove scanner effects in multi-site imaging data

    Arguments
    ---------
    dat : a pandas data frame or numpy array
        - neuroimaging data to correct with shape = (features, samples) e.g. cortical thickness measurements, image voxels, etc

    covars : a pandas data frame w/ shape = (samples, covariates)
        - contains the batch/scanner covariate as well as additional covariates (optional) that should be preserved during harmonization.
        
    batch_col : string
        - indicates batch (scanner) column name in covars (e.g. "scanner")

    categorical_cols : list of strings
        - specifies column names in covars data frame of categorical variables to be preserved during harmonization (e.g. ["sex", "disease"])

    continuous_cols : list of strings
        - indicates column names in covars data frame of continuous variables to be preserved during harmonization (e.g. ["age"])

    eb : should Empirical Bayes be performed?
        - True by default

    parametric : should parametric adjustements be performed?
        - True by default

    mean_only : should only be the mean adjusted (no scaling)?
        - False by default

    ref_batch : batch (site or scanner) to be used as reference for batch adjustment.
        - None by default
        
    Returns
    -------
    A dictionary of length 3:
    - data: A numpy array with the same shape as `dat` which has now been ComBat-harmonized
    - estimates: A dictionary of the ComBat estimates used for harmonization
    - info: A dictionary of the inputs needed for ComBat harmonization
    """
    ##############################
    ### CLEANING UP INPUT DATA ###
    ##############################
    if not isinstance(covars, pd.DataFrame):
        raise ValueError('covars must be pandas dataframe -> try: covars = pandas.DataFrame(covars)')

    if not isinstance(categorical_cols, (list,tuple)):
        if categorical_cols is None:
            categorical_cols = []
        else:
            categorical_cols = [categorical_cols]
    if not isinstance(continuous_cols, (list,tuple)):
        if continuous_cols is None:
            continuous_cols = []
        else:
            continuous_cols = [continuous_cols]
    
    if isinstance(dat, pd.DataFrame):
       dat = np.array(dat, dtype='float32')

    batch_col_1=batch_col
    covars_pd=covars.copy()
    batch_original=np.unique(np.array(covars_pd.loc[:,(batch_col_1)].copy(), dtype="int"))
    print(batch_original)
    #batch_original=np.unique(np.array(covars_pd[[batch_col_1]], dtype="str"))

    ref_level,batch_col, cat_cols, num_cols, covar_labels, covars= shape_data(ref_batch,covars,batch_col,categorical_cols,continuous_cols)
    # create dictionary that stores batch info
    (batch_levels, sample_per_batch) = np.unique(covars[:,batch_col],return_counts=True)
    

     # create design matrix
    print('[neuroCombat] Creating design matrix')
    design = make_design_matrix(covars_pd, batch_col_1, categorical_cols, continuous_cols, ref_batch)
    
    batch_info=[list(np.where(covars[:,batch_col]==idx)[0]) for idx in batch_levels]

    info_dict = {
        'batch_levels': batch_levels,
        'ref_level': ref_level,
        'n_batch': len(batch_levels),
        'n_sample': int(covars.shape[0]),
        'sample_per_batch': sample_per_batch.astype('int'),
        'batch_info': batch_info,
        'design': design
    }

   
    # standardize data across features
    print('[neuroCombat] Standardizing data across features')
    s_data, s_mean, v_pool, mod_mean, B_hat = standardize_across_features(dat, design, info_dict)
    
    # Added here to save espefically mod_mean_ref for later combat_transform 
    if ref_level is not None:
      mod_mean_ref=mod_mean[:, batch_info[ref_level]].copy()
    else:
      mod_mean_ref=None
      
    # fit L/S models and find priors
    print('[neuroCombat] Fitting L/S model and finding priors')
    LS_dict = fit_LS_model_and_find_priors(s_data, design, info_dict, mean_only)

    # find parametric adjustments
    if eb:
        if parametric:
            print('[neuroCombat] Finding parametric adjustments')
            gamma_star, delta_star = find_parametric_adjustments(s_data, LS_dict, info_dict, mean_only)
        else:
            print('[neuroCombat] Finding non-parametric adjustments')
            gamma_star, delta_star = find_non_parametric_adjustments(s_data, LS_dict, info_dict, mean_only)
    else:
        print('[neuroCombat] Finding L/S adjustments without Empirical Bayes')
        gamma_star, delta_star = find_non_eb_adjustments(s_data, LS_dict, info_dict)

    # adjust data
    print('[neuroCombat] Final adjustment of data')
    bayes_data = adjust_data_final(s_data, design, gamma_star, delta_star, 
                                    s_mean, mod_mean, v_pool, info_dict,dat)

    bayes_data = np.array(bayes_data)
    estimates = {'ref_batch': ref_batch,'batch_ori':batch_original,'batches': info_dict['batch_levels'], 'var.pooled': v_pool, 'stand.mean': s_mean, 'mod.mean': mod_mean, 'mod.mean_ref':mod_mean_ref,'gamma.star': gamma_star, 'delta.star': delta_star, 'B_hat': B_hat, 'training_design': design}
    estimates = {**LS_dict, **estimates, }

    return {
        'data': bayes_data,
        'estimates': estimates,
        'info': info_dict
    }


def shape_data(ref_batch,covars,batch_col,categorical_cols,continuous_cols):
  
  covar_labels = np.array(covars.columns) #array(['batch', 'age', 'gender', 'TIV'], dtype=object)
  covars = np.array(covars, dtype='object') 

  ##############################

  # get column indices for relevant variables

  batch_col = np.where(covar_labels==batch_col)[0][0]
  cat_cols = [np.where(covar_labels==c_var)[0][0] for c_var in categorical_cols]
  num_cols = [np.where(covar_labels==n_var)[0][0] for n_var in continuous_cols]

  # convert batch col to integer
  if ref_batch is None:
      ref_level=None
  else:
      ref_indices = np.argwhere(covars[:, batch_col] == ref_batch).squeeze()
      if ref_indices.shape[0]==0:
          ref_level=None
          ref_batch=None
          print('[neuroCombat] batch.ref not found. Setting to None.')
          covars[:,batch_col] = np.unique(covars[:,batch_col],return_inverse=True)[-1] 
          # return_inverse gives the batch array offset to zero. eg: unique batch = 1,3,4,7
          # return_inverse returns the batch array = [0,0,0,0,0,..., 1,1,1,...,2,2,2,2...] instead of [1, 1, 1, ,1,..., 3,3,3,3...]
      else:
          covars[:,batch_col] = np.unique(covars[:,batch_col],return_inverse=True)[-1] 
          ref_level = covars[np.int(ref_indices[0]),batch_col] #the ref_level is the batch id corresponding to the new off-set format of the batch array
          #if batch_ref was 2, the ref_level is now 1

  return ref_level,batch_col, cat_cols, num_cols, covar_labels, covars

def make_design_matrix(covars, batch_col, categorical_cols, continuous_cols, ref_batch): #CHANGE HERE: make_design should be use for applying weights
    """
    Return Matrix containing the following parts:
        - one-hot matrix of batch variable (full)
        - one-hot matrix for each categorical_cols (removing the first column)
        - column for each continuous_cols
    """
    # I repeat the verification of this data, for the test set application
    if not isinstance(covars, pd.DataFrame):
      raise ValueError('covars must be pandas dataframe -> try: covars = pandas.DataFrame(covars)')

    if not isinstance(categorical_cols, (list,tuple)):
        if categorical_cols is None:
            categorical_cols = []
        else:
            categorical_cols = [categorical_cols]
    if not isinstance(continuous_cols, (list,tuple)):
        if continuous_cols is None:
            continuous_cols = []
        else:
            continuous_cols = [continuous_cols]

    # The covars input for make_design is always a dataframe, 
    # thus we have to repeat the shape_data step, 
    # so that it can be used for the test set as well
    ref_level,batch_col, cat_cols, num_cols, covar_labels, covars= shape_data(ref_batch,covars,batch_col,categorical_cols,continuous_cols)

 #_____covariates should be a np from down here________________

    def to_categorical(y, nb_classes=None):
        if not nb_classes:
            nb_classes = np.max(y)+1
        Y = np.zeros((len(y), nb_classes))
        for i in range(len(y)):
            Y[i, y[i]] = 1.
        return Y
    
    hstack_list = []

    ### batch one-hot ###
    # convert batch column to integer in case it's string
    batch = np.unique(covars[:,batch_col],return_inverse=True)[-1] #returns batch variable offset to zero [0,0,0,0,1,1,1...]
    batch_onehot = to_categorical(batch, len(np.unique(batch))) #dummy variable of batch before
    if ref_level is not None:
        batch_onehot[:,ref_level] = np.ones(batch_onehot.shape[0]) #I go to the column corresponding to the batch_ref and substitute everything by ones
    hstack_list.append(batch_onehot) #They sinalize ref_batch by putting all column to 1 

    ### categorical one-hots ###
    for cat_col in cat_cols:
        cat = np.unique(np.array(covars[:,cat_col]),return_inverse=True)[1]
        cat_onehot = to_categorical(cat, len(np.unique(cat)))[:,1:]
        hstack_list.append(cat_onehot)

    ### numerical vectors ###
    for num_col in num_cols:
        num = np.array(covars[:,num_col],dtype='float32')
        num = num.reshape(num.shape[0],1)
        hstack_list.append(num)

    design = np.hstack(hstack_list)
    return design

def standardize_across_features(X, design, info_dict):
    n_batch = info_dict['n_batch']
    n_sample = info_dict['n_sample']
    sample_per_batch = info_dict['sample_per_batch']
    batch_info = info_dict['batch_info']
    ref_level = info_dict['ref_level']

    def get_beta_with_nan(yy, mod):
        wh = np.isfinite(yy)
        mod = mod[wh,:]
        yy = yy[wh]
        B = np.dot(np.dot(la.inv(np.dot(mod.T, mod)), mod.T), yy.T)
        return B

    betas = []
    for i in range(X.shape[0]):
        betas.append(get_beta_with_nan(X[i,:], design))
    B_hat = np.vstack(betas).T
    
    #B_hat = np.dot(np.dot(la.inv(np.dot(design.T, design)), design.T), X.T)
    if ref_level is not None:
        grand_mean = np.transpose(B_hat[ref_level,:])
    else:
        grand_mean = np.dot((sample_per_batch/ float(n_sample)).T, B_hat[:n_batch,:])
    stand_mean = np.dot(grand_mean.T.reshape((len(grand_mean), 1)), np.ones((1, n_sample)))
    #var_pooled = np.dot(((X - np.dot(design, B_hat).T)**2), np.ones((n_sample, 1)) / float(n_sample))

    if ref_level is not None:
        X_ref = X[:,batch_info[ref_level]]
        design_ref = design[batch_info[ref_level],:]
        n_sample_ref = sample_per_batch[ref_level]
        var_pooled = np.dot(((X_ref - np.dot(design_ref, B_hat).T)**2), np.ones((n_sample_ref, 1)) / float(n_sample_ref))
    else:
        var_pooled = np.dot(((X - np.dot(design, B_hat).T)**2), np.ones((n_sample, 1)) / float(n_sample))

    var_pooled[var_pooled==0] = np.median(var_pooled!=0)
    
    mod_mean = 0
    if design is not None:
        tmp = copy.deepcopy(design)
        tmp[:,range(0,n_batch)] = 0
        mod_mean = np.transpose(np.dot(tmp, B_hat))
    ######### Continue here. 


    #tmp = np.array(design.copy())
    #tmp[:,:n_batch] = 0
    #stand_mean  += np.dot(tmp, B_hat).T

    s_data = ((X- stand_mean - mod_mean) / np.dot(np.sqrt(var_pooled), np.ones((1, n_sample))))

    return s_data, stand_mean, var_pooled, mod_mean, B_hat

def aprior(delta_hat):
    m = np.mean(delta_hat)
    s2 = np.var(delta_hat,ddof=1)
    return (2 * s2 +m**2) / float(s2)

def bprior(delta_hat):
    m = delta_hat.mean()
    s2 = np.var(delta_hat,ddof=1)
    return (m*s2+m**3)/s2

def postmean(g_hat, g_bar, n, d_star, t2):
    return (t2*n*g_hat+d_star * g_bar) / (t2*n+d_star)

def postvar(sum2, n, a, b):
    return (0.5 * sum2 + b) / (n / 2.0 + a - 1.0)

def convert_zeroes(x):
    x[x==0] = 1
    return x

def fit_LS_model_and_find_priors(s_data, design, info_dict, mean_only):
    n_batch = info_dict['n_batch']
    batch_info = info_dict['batch_info'] 
    
    batch_design = design[:,:n_batch]
    gamma_hat = np.dot(np.dot(la.inv(np.dot(batch_design.T, batch_design)), batch_design.T), s_data.T)

    delta_hat = []
    for i, batch_idxs in enumerate(batch_info):
        if mean_only:
            delta_hat.append(np.repeat(1, s_data.shape[0]))
        else:
            delta_hat.append(np.var(s_data[:,batch_idxs],axis=1,ddof=1))
    
    delta_hat = list(map(convert_zeroes,delta_hat))
    gamma_bar = np.mean(gamma_hat, axis=1) 
    t2 = np.var(gamma_hat,axis=1, ddof=1)

    if mean_only:
        a_prior = None
        b_prior = None
    else:
        a_prior = list(map(aprior, delta_hat))
        b_prior = list(map(bprior, delta_hat))

    LS_dict = {}
    LS_dict['gamma_hat'] = gamma_hat
    LS_dict['delta_hat'] = delta_hat
    LS_dict['gamma_bar'] = gamma_bar
    LS_dict['t2'] = t2
    LS_dict['a_prior'] = a_prior
    LS_dict['b_prior'] = b_prior
    return LS_dict

#Helper function for parametric adjustements:
def it_sol(sdat, g_hat, d_hat, g_bar, t2, a, b, conv=0.0001):
    n = (1 - np.isnan(sdat)).sum(axis=1)
    g_old = g_hat.copy()
    d_old = d_hat.copy()

    change = 1
    count = 0
    while change > conv:
        g_new = postmean(g_hat, g_bar, n, d_old, t2)
        sum2 = ((sdat - np.dot(g_new.reshape((g_new.shape[0], 1)), np.ones((1, sdat.shape[1])))) ** 2).sum(axis=1)
        d_new = postvar(sum2, n, a, b)

        change = max((abs(g_new - g_old) / g_old).max(), (abs(d_new - d_old) / d_old).max())
        g_old = g_new #.copy()
        d_old = d_new #.copy()
        count = count + 1
    adjust = (g_new, d_new)
    return adjust 



#Helper function for non-parametric adjustements:
def int_eprior(sdat, g_hat, d_hat):
    r = sdat.shape[0]
    gamma_star, delta_star = [], []
    for i in range(0,r,1):
        g = np.delete(g_hat,i)
        d = np.delete(d_hat,i)
        x = sdat[i,:]
        n = x.shape[0]
        j = np.repeat(1,n)
        A = np.repeat(x, g.shape[0])
        A = A.reshape(n,g.shape[0])
        A = np.transpose(A)
        B = np.repeat(g, n)
        B = B.reshape(g.shape[0],n)
        resid2 = np.square(A-B)
        sum2 = resid2.dot(j)
        LH = 1/(2*math.pi*d)**(n/2)*np.exp(-sum2/(2*d))
        LH = np.nan_to_num(LH)
        gamma_star.append(sum(g*LH)/sum(LH))
        delta_star.append(sum(d*LH)/sum(LH))
    adjust = (gamma_star, delta_star)
    return adjust


def find_parametric_adjustments(s_data, LS, info_dict, mean_only):
    batch_info  = info_dict['batch_info'] 
    ref_level = info_dict['ref_level']

    gamma_star, delta_star = [], []
    for i, batch_idxs in enumerate(batch_info):
        if mean_only:
            gamma_star.append(postmean(LS['gamma_hat'][i], LS['gamma_bar'][i], 1, 1, LS['t2'][i]))
            delta_star.append(np.repeat(1, s_data.shape[0]))
        else:
            temp = it_sol(s_data[:,batch_idxs], LS['gamma_hat'][i],
                        LS['delta_hat'][i], LS['gamma_bar'][i], LS['t2'][i], 
                        LS['a_prior'][i], LS['b_prior'][i])
            gamma_star.append(temp[0])
            delta_star.append(temp[1])

    gamma_star = np.array(gamma_star)
    delta_star = np.array(delta_star)

    if ref_level is not None:
        gamma_star[ref_level,:] = np.zeros(gamma_star.shape[-1]) 
        delta_star[ref_level,:] = np.ones(delta_star.shape[-1]) 

    return gamma_star, delta_star

def find_non_parametric_adjustments(s_data, LS, info_dict, mean_only):
    batch_info  = info_dict['batch_info'] 
    ref_level = info_dict['ref_level']

    gamma_star, delta_star = [], []
    for i, batch_idxs in enumerate(batch_info):
        if mean_only:
            LS['delta_hat'][i] = np.repeat(1, s_data.shape[0])
        temp = int_eprior(s_data[:,batch_idxs], LS['gamma_hat'][i],
                    LS['delta_hat'][i])

        gamma_star.append(temp[0])
        delta_star.append(temp[1])

    gamma_star = np.array(gamma_star)
    delta_star = np.array(delta_star)

    if ref_level is not None:
        gamma_star[ref_level,:] = np.zeros(gamma_star.shape[-1]) 
        delta_star[ref_level,:] = np.ones(delta_star.shape[-1]) 

    return gamma_star, delta_star

def find_non_eb_adjustments(s_data, LS, info_dict):
    gamma_star = np.array(LS['gamma_hat'])
    delta_star = np.array(LS['delta_hat'])
    ref_level = info_dict['ref_level']
    
    if ref_level is not None:
        gamma_star[ref_level,:] = np.zeros(gamma_star.shape[-1]) 
        delta_star[ref_level,:] = np.ones(delta_star.shape[-1])
    
    return gamma_star, delta_star

def adjust_data_final(s_data, design, gamma_star, delta_star, stand_mean, mod_mean, var_pooled, info_dict, dat):
    sample_per_batch = info_dict['sample_per_batch']
    n_batch = info_dict['n_batch']
    n_sample = info_dict['n_sample']
    batch_info = info_dict['batch_info']
    ref_level = info_dict['ref_level']

    batch_design = design[:,:n_batch]

    bayesdata = s_data
    gamma_star = np.array(gamma_star)
    delta_star = np.array(delta_star)

    for j, batch_idxs in enumerate(batch_info):
        dsq = np.sqrt(delta_star[j,:])
        dsq = dsq.reshape((len(dsq), 1))
        denom = np.dot(dsq, np.ones((1, sample_per_batch[j])))
        numer = np.array(bayesdata[:,batch_idxs] - np.dot(batch_design[batch_idxs,:], gamma_star).T)

        bayesdata[:,batch_idxs] = numer / denom

    vpsq = np.sqrt(var_pooled).reshape((len(var_pooled), 1))
    bayesdata = bayesdata * np.dot(vpsq, np.ones((1, n_sample))) + stand_mean + mod_mean

    if ref_level is not None:
        bayesdata[:, batch_info[ref_level]] = dat[:,batch_info[ref_level]] # Put the original data back just for the reference batch subjects

    return bayesdata


def neuroCombat_transform(dat,covars, batch_col, cat_cols, num_cols,estimates): #covars_train[['batch']]
    """
    Combat harmonization with pre-trained ComBat estimates [UNDER DEVELOPMENT]

    Arguments
    ---------
    dat : a pandas data frame or numpy array for the new dataset to harmonize
        - rows must be identical to the training dataset
    
    batch : numpy array specifying scanner/batch for the new dataset
        - scanners/batches must also be present in the training dataset

    estimates : dictionary of ComBat estimates from a previously-harmonized dataset
        - should be in the same format as neuroCombat(...)['estimates']
        
    Returns
    -------
    A dictionary of length 2:
    - data: A numpy array with the same shape as `dat` which has now been ComBat-harmonized
    - estimates: A dictionary of the ComBat estimates used for harmonization
    """
    batch=covars[['batch']]
    ref_level=None

    if not isinstance(num_cols, (list,tuple)):
      if num_cols is None:
        num_cols = []
      else:
        num_cols = [num_cols]
    if not isinstance(num_cols, (list,tuple)):
      if num_cols is None:
        num_cols = []
      else:
        num_cols = [num_cols]

    
    batch_int=np.unique(batch) #batch in integer format
    batch=list(map(int, np.array(batch)))
    batch = np.array(batch, dtype="str") # put batch array as string
    new_levels = np.unique(batch) # levels of batch for test set
    print('Batchs for this set {}'.format(new_levels))
    old_levels=list(map(int, estimates['batches']))
    old_levels = np.array(old_levels, dtype="str") # levels of batch for training set
    print('Batchs from the training set estimation {}'.format(old_levels))
    if estimates['ref_batch'] is not None: #' I need to reshape batch_levels as in the training set? 
      print('M-ComBat option was used during fitting')
      old_levels=estimates['batch_ori'] #the original batch levels without the reshape 
      old_levels = np.array(old_levels, dtype="str")

      missing_levels = np.setdiff1d(new_levels, old_levels)
      if missing_levels.shape[0] != 0:
          raise ValueError("The batches " + str(missing_levels) +
                         " do not have estimated parameters to be applied")
          
      ref_batch=estimates['ref_batch'] 
      if (ref_batch in batch_int): #if the reference batch is in the new batch levels
        ref_level=np.where(batch_int==ref_batch)[0][0] 
        #the index of the reference batch in the new batch levels. 
        #eg: if batch_new =[0 2 3 5 9], ref_batch= 3, ref_level=2
      
    else: #'
      missing_levels = np.setdiff1d(new_levels, old_levels) #batch levels as str type
      if missing_levels.shape[0] != 0:
          raise ValueError("The batches " + str(missing_levels) +
                         " are not part of the training dataset")


    wh = [int(np.where(old_levels==x)[0]) if x in old_levels else None for x in batch]

    # if new batch is in old levels what is the index position for estimates data arrays 
    #eg: batch_new=2, exists in old levels in [0 2 3 5 9] is index position 1, then, 
    #the wh will have the id 1 repeated for the same number of subjects that belong to this batch
    #[1 1 1 1 1 1 1 1]
    
    var_pooled = estimates['var.pooled'] #shape (120,1)
    stand_mean = estimates['stand.mean']#[:, 0] #the original shape is (120,n_training_samples)
    mod_mean = estimates['mod.mean']
    mod_mean_ref= estimates['mod.mean_ref']
    gamma_star = estimates['gamma.star']
    delta_star = estimates['delta.star']
    B_hat=estimates['B_hat']
    training_design=estimates['training_design']
    n_array = dat.shape[1]   

    batch_info=[list(np.where(batch==x)[0]) if x in old_levels else None for x in new_levels]
    #a list of lists with the subject index for each batch [[ 0 1 2 3 4 ...] [50 51 52 ...]]
    
    
    (batch_levels, sample_per_batch) = np.unique(batch,return_counts=True)
    
    n_batch=int(batch_levels.shape[0])

    n_sample=int(batch.shape[0])


    design=make_design_matrix(covars, batch_col, cat_cols, num_cols, ref_batch=None) 
    #here ref_batch is none because we don't need to signaling which is the ref_batch for the estimating process


    batch_design = design[:,:n_batch]

    batch_available= np.unique(wh)
    print('Batches in current set matching the ones from training set estimation {}'.format(batch_available))

    n_batch_old_levels=int(old_levels.shape[0])
    B_hat_batch=B_hat[:n_batch_old_levels,:].copy() #I select the B_hat only for batch

    B_hat_batch=B_hat_batch[batch_available,:] 
    #I need to select B_hat coef for the existing batches + for the covariates 
    #delete the batch_columns from B_hat that are not present in the test set
    B_hat_apply=np.concatenate((B_hat_batch,B_hat[n_batch_old_levels:,:]))
    
    # Steps:
    # 1. Check if we are in the case of M-ComBat or ComBat
    # 1.1 IF M-ComBat: check if we are transforming the reference training set OR a new test set by seeing mod_mean_estimates == new_mod_mean
    # 1.2 IF normal ComBat: check wether we are transforming the training set OR test set 

    new_mod_mean = 0
    if design is not None:
        tmp = copy.deepcopy(design)
        tmp[:,range(0,n_batch)] = 0
        new_mod_mean = np.transpose(np.dot(tmp, B_hat_apply))

    # Use old design matrix to discover the old subjects belonging to ref level
    #training_design_ref=training_design[:,ref_level] # training design matrix (n_subj x n_cov: n_batchs + n_biocov)
    #training_ref_id=np.where(training_design_ref==1)[0]
    
    # np.dot(np.sqrt(var_pooled), np.ones((1, n_sample))))
    # vpsq = np.sqrt(var_pooled).reshape((len(var_pooled), 1))
    # var_pooled
    
    if mod_mean_ref is not None: # Usage of M-ComBat
      
      if ref_level is not None: # The reference site is in the current site we are transforming

        if ref_level==0:
          after_ref_col=training_design[:,ref_level+1] # training design matrix (n_subj x n_cov: n_batchs + n_biocov)
          last_training_ref_id=np.where(after_ref_col==1)[0][0]
          training_design_ref=training_design[:last_training_ref_id,:]
          training_ref_id=np.arange(0,last_training_ref_id)

        else:
          after_ref_col=training_design[:,ref_level+1] # training design matrix (n_subj x n_cov: n_batchs + n_biocov)
          last_training_ref_id=np.where(after_ref_col==1)[0][0]

          before_ref_col=training_design[:,ref_level-1] # training design matrix (n_subj x n_cov: n_batchs + n_biocov)
          first_training_ref_id=np.where(before_ref_col==1)[0][-1]
          training_design_ref=training_design[first_training_ref_id:last_training_ref_id,:]

          training_ref_id=np.arange(first_training_ref_id,last_training_ref_id)

        new_subj_id_from_ref=batch_info[ref_level] # The index from this set which subjects belonging to reference site


        if mod_mean_ref.shape==new_mod_mean[:,new_subj_id_from_ref].shape: # check wether we are transforming the reference data or new data coming from reference site

          if np.all( mod_mean_ref==new_mod_mean[:,new_subj_id_from_ref]): # We are transforming the reference training set

            # The standardize data will be put here

            s_data=np.zeros((new_mod_mean.shape[0],new_mod_mean.shape[1]))

            print( 'Transforming tthe reference and other sets used in the combat estimation') # The reference data at the end will be putted as in the original input
            
            n_sample_ref=mod_mean_ref.shape[1]
            stand_mean_ref=stand_mean[:,range(0,n_sample_ref)].copy() # get the stand mean for all features for the same amount of subjects as ref
            
            stand_mean_1 = stand_mean_ref+ mod_mean_ref # We are using the mod_mean from reference
            
            s_data_train = np.subtract(dat[:,training_ref_id], stand_mean_1)/np.sqrt(var_pooled) # The standardization with mod_mean from training

            # Transforming the other data that is not the reference set with the mod_mean.mean()
            
            new_subj_id_not_ref=[sublist for i,sublist in enumerate(batch_info) if i!=ref_level]
            new_subj_id_not_ref=np.array(new_subj_id_not_ref,dtype=object) # convert a list of list into 2D array
            new_subj_id_not_ref=np.hstack(new_subj_id_not_ref) # convert to 1D array

            n_array_test = dat[:, new_subj_id_not_ref].shape[1]

            stand_mean_2 = stand_mean[:,0]+mod_mean_ref.mean(axis=1) #We are using the mod_mean from training
            stand_mean_2 = np.transpose([stand_mean_2, ]*n_array_test)
            s_data_test = np.subtract(dat[:, new_subj_id_not_ref], stand_mean_2)/np.sqrt(var_pooled) # The standardization with mod_mean from training

            # The train data and test data will go in the same place as in the input of this function
            s_data[:,training_ref_id]=s_data_train
            s_data[:,new_subj_id_not_ref]=s_data_test

            stand_mean=np.zeros((new_mod_mean.shape[0],new_mod_mean.shape[1]))
            stand_mean[:,training_ref_id]=stand_mean_1
            stand_mean[:,new_subj_id_not_ref]=stand_mean_2

          else: # Transforming a test set that contains data from reference site, using reference M-ComBat estimations
            print('Transforming a test set with reference estimations')

            stand_mean = stand_mean[:,0]+mod_mean_ref.mean(axis=1) # We will use the average of the mod_mean from reference
            stand_mean = np.transpose([stand_mean, ]*n_array)
            s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from ref

            # the part of data that is coming from reference site will be replace to original at the end

        else: # Transforming a test set that contains data from reference site, using reference M-ComBat estimations
          print('Transforming a test set with reference estimations')

          stand_mean = stand_mean[:,0]+mod_mean_ref.mean(axis=1) # We will use the average of the mod_mean from ref
          stand_mean = np.transpose([stand_mean, ]*n_array)
          s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from ref
          
          # the part of data that is coming from reference site will be replace to original at the end

      else: # We are transforming new data not using for estimations but still using reference estimations
          
          print('Transforming a test set with reference estimations')
          stand_mean = stand_mean[:,0]+mod_mean_ref.mean(axis=1) # We will use the average of the mod_mean from ref
          stand_mean = np.transpose([stand_mean, ]*n_array)
          s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from ref
          
    else: # Normal ComBat - no reference batch used
        
        if mod_mean.shape==new_mod_mean.shape: # the mod_mean calculated now is the same shape of the mod_mean used in estimation part
       
          if np.all(mod_mean==new_mod_mean): # if the mod_mean info is exactly the same, then we are transforming the training set
            
            print('Transforming a training set')
            stand_mean = stand_mean+ mod_mean # We are using the mod_mean from training
            s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from training

          else:
            print('Transforming a test set')
            stand_mean = stand_mean[:,0]+mod_mean.mean(axis=1) # We will use the average of the mod_mean from training
            stand_mean = np.transpose([stand_mean, ]*n_array)
            s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from training


        else:
          print('Transforming a test set')
          stand_mean = stand_mean[:,0]+mod_mean.mean(axis=1) # We will use the average of the mod_mean from training
          stand_mean = np.transpose([stand_mean, ]*n_array)
          s_data = np.subtract(dat, stand_mean)/np.sqrt(var_pooled) # The standardization with mod_mean from training

    bayesdata= s_data
    gamma = gamma_star[batch_available,:] #wh #after this, gamma and delta will only have the estimates of the batches in the test set
    #eg: if batch test is [ 1 2] and batch train was[ 1 2 3 4 5], gamma and delta are only keeping the estimates for [1 2]
    delta = delta_star[batch_available,:] #wh

    #sample_per_batch.astype('int')

    for j, batch_idxs in enumerate(batch_info): # j is incrementing for each batch
      # batch_indx is the subject indexes for batch j

      dsq = np.sqrt(delta[j,:])
      dsq = dsq.reshape((len(dsq), 1))
      denom = np.dot(dsq, np.ones((1, sample_per_batch[j])))
      numer = np.array(bayesdata[:,batch_idxs] - np.dot(batch_design[batch_idxs,:], gamma).T) #gamma_start 
      #we do np.dot(batch_design, gamma) because we are adjusting data batch to batch

      bayesdata[:,batch_idxs] = numer / denom # for each group of subjects belonging to batch j we calculate this
    
    bayesdata_=bayesdata.copy() # the corrected data: without biocovariates and standardized

    # unstandardization
    
    #vpsq = np.sqrt(var_pooled).reshape((len(var_pooled), 1))
    
    bayesdata = bayesdata*np.sqrt(var_pooled) + stand_mean # unstandardization

    if ref_level is not None:
        print(' Reintroducing original data for all data from reference site')
        # EITHER in the case of ref_level existing and corresponding to the original data used for estimation OR 
        # the case that it's new test data but coming from ref site, we should replace with the original data because 
        # the harmonization will be for all other sets to the level of ref      
        
        bayesdata_[:, batch_info[ref_level]]= s_data[:, batch_info[ref_level]] # For the reference set the corrected data is equal to the s_data
        bayesdata[:, batch_info[ref_level]] = dat[:,batch_info[ref_level]] # Put the original data back just for the reference batch subjects

    out = {
        'data': bayesdata,
        'estimates': estimates,
        'data_without_biocov': bayesdata_
    }
    
    return out