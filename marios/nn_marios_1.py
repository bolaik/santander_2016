import numpy as np
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import roc_auc_score
from collections import defaultdict
from keras.layers.advanced_activations import PReLU
from keras.layers.normalization import BatchNormalization
from keras.regularizers import *
from sklearn.utils import shuffle
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.utils import np_utils
from keras import optimizers
import keras

epc=100
batch=512

def build_model(input_dim, output_dim):
    models = Sequential()

    models.add(Dense(120, input_dim=input_dim, init='uniform', W_regularizer=l2(0.00001)))
    models.add(PReLU())
    models.add(BatchNormalization())
    models.add(Dropout(0.6))
    models.add(Dense(output_dim, init='uniform'))
    models.add(Activation('softmax'))

    opt = optimizers.Adagrad(lr=0.0125)
    models.compile(loss='binary_crossentropy', optimizer=opt)
    return models

def loadcolumn(filename,col=4, skip=1, floats=True):
    pred=[]
    op=open(filename,'r')
    if skip==1:
        op.readline() #header
    for line in op:
        line=line.replace('\n','')
        sps=line.split(',')
        #load always the last columns
        if floats:
            pred.append(float(sps[col]))
        else :
            pred.append(str(sps[col]))
    op.close()
    return np.array(pred)            

    
def load_datas(filename):

    return joblib.load(filename)

def printfile(X, filename):

    joblib.dump((X), filename)
    
def printfilcsve(X, filename, headers):

    np.savetxt(filename,X, header=headers) 

    
    
def load_ids(id_file, cols=20):
    verybiglist=[]
    for s in range(0,cols):
        idss=loadcolumn(id_file,col=s, skip=1, floats=True)
        id_list=[ [] ,[] , [], [] , []]
        id_dict=[ defaultdict(int) ,defaultdict(int) , defaultdict(int), defaultdict(int) , defaultdict(int)]
        for g in range(0,len(idss)):
            id_list[int(idss[g])].append(g)
            id_dict[int(idss[g])][g]=1
        biglist=[]
        for k in range(5):
            training_ids=[s for s in range(0,len(idss)) if s not in id_dict[k] ]
            biglist.append([training_ids,id_list[k] ])
            print(len(biglist), len(biglist[0]))
        verybiglist.append(biglist)
            
    return verybiglist
    
    


def all_load_vecorizerr(tr,te,drop=["ind_var2_0","ind_var2","ind_var27_0","ind_var28_0","ind_var28","ind_var27",
"ind_var41","ind_var46_0","ind_var46","num_var27_0","num_var28_0","num_var28","num_var27","num_var41","num_var46_0",
"num_var46","saldo_var28","saldo_var27","saldo_var41","saldo_var46","imp_amort_var18_hace3","imp_amort_var34_hace3",
"imp_reemb_var13_hace3","imp_reemb_var33_hace3","imp_trasp_var17_out_hace3","imp_trasp_var33_out_hace3",
"num_var2_0_ult1","num_var2_ult1","num_reemb_var13_hace3","num_reemb_var33_hace3","num_trasp_var17_out_hace3",
"num_trasp_var33_out_hace3","saldo_var2_ult1","saldo_medio_var13_medio_hace3","ind_var6_0","ind_var6",
"ind_var13_medio_0","ind_var18_0","ind_var26_0","ind_var25_0","ind_var32_0","ind_var34_0","ind_var37_0",
"ind_var40","num_var6_0","num_var6","num_var13_medio_0","num_var18_0","num_var26_0","num_var25_0","num_var32_0",
"num_var34_0","num_var37_0","num_var40","saldo_var6","saldo_var13_medio","delta_imp_reemb_var13_1y3",
"delta_imp_reemb_var17_1y3","delta_imp_reemb_var33_1y3","delta_imp_trasp_var17_in_1y3","delta_imp_trasp_var17_out_1y3",
"delta_imp_trasp_var33_in_1y3","delta_imp_trasp_var33_out_1y3"]):

    train  = pd.read_csv(tr, sep=',',quotechar='"')
    test  = pd.read_csv(te, sep=',',quotechar='"')
    train.drop('ID', axis=1, inplace=True)
    train.drop('TARGET', axis=1, inplace=True)    
    test.drop('ID', axis=1, inplace=True)
    for name in drop:
        train.drop(name, axis=1, inplace=True)    
        test.drop(name, axis=1, inplace=True)        

    train['zerocount'] = train.apply(lambda x: np.sum(x == 0), axis=1)
    test['zerocount'] = test.apply(lambda x: np.sum(x == 0), axis=1)

    train['var38'].replace(117310.979016494, -1.0, inplace=True)
    test ['var38'].replace(117310.979016494, -1.0, inplace=True)
    
    train_s = train
    test_s = test
    result = pd.concat([test_s,train_s])
    
    #test_s.drop('id', axis=1, inplace=True)
    result=result.T.to_dict().values()
    train = train_s.T.to_dict().values()
    test = test_s.T.to_dict().values()
    
    vec = DictVectorizer()
    vec.fit(result)
    train = vec.transform(train)
    test = vec.transform(test)
    
    print train.shape
    print test.shape    
    
    
    return train,test

def bagged_set(X,y, seed, estimators, xt, nval=0.0, verbos=0): 
  
   baggedpred=[ 0.0 for d in range(0, xt.shape[0])] 
           
   for i in range (0, estimators): 
        
        X_t,y_c=shuffle(X,y, random_state=seed+i) 
        np.random.seed(seed+i)
        model = build_model(xt.shape[1], 2)
        if nval>0.0:
            x_train_oof, x_valid_oof, y_train_oof_nn, y_valid_oof_nn = cross_validation.train_test_split(
            X_t, y_c, test_size=nval, random_state=i*seed)
            model.fit(x_train_oof,np_utils.to_categorical( y_train_oof_nn),
                      nb_epoch=epc, batch_size=batch,
                      validation_data=(x_valid_oof,np_utils.to_categorical(y_valid_oof_nn)), 
                    verbose=verbos, callbacks=[MonitorAUC(x_valid_oof,y_valid_oof_nn)])
        else :
            y_train_oof_nn = np_utils.to_categorical(y_c)
            model.fit(X_t, y_train_oof_nn, nb_epoch=epc, batch_size=batch, verbose=verbos)

         
        preds =model.predict_proba(xt) [:,1]
 
        for j in range (0, xt.shape[0]):            
                 baggedpred[j]+=preds[j] 
        #print("finshed bag %d" % (i+1)) 
                
   for j in range (0, len(baggedpred)):         
                baggedpred[j]/=float(estimators) 
                
   return np.array(baggedpred) 



    
def main():
    
  
        load_data=True      
        metafolder_train="data/output/train/"
        metafolder_test="data/output/test/"        
        input_folder="data/input/"
        feature_folder="data/output/features/"
        SEED=15
        outset="nn_marios_1" # predic of all files
        number_of_folds=5 # repeat the CV procedure 10 times to get more precise results       
        
        ######### Load files ############

        y=loadcolumn(input_folder+ "train.csv",col=370, skip=1, floats=True)
        ids=loadcolumn(input_folder+ "test.csv",col=0, skip=1, floats=True)
        idstrain=loadcolumn(input_folder+ "train.csv",col=0, skip=1, floats=True)
        keepfold=[0 for k in range(len(y))]
        
        if load_data:
            X,X_test=all_load_vecorizerr(input_folder+'train.csv',input_folder+'test.csv') 
            printfile(X,"Xvector.pkl")  
            printfile(X_test,"Xtestvector.pkl")                               
            X=load_datas("Xvector.pkl").toarray()
            X_test=load_datas("Xtestvector.pkl").toarray()


        tsn_features=(np.loadtxt(feature_folder+ "tsne_feats.csv", delimiter=",", skiprows=1, usecols=[1,2]))
        
        tsn_features_train=tsn_features[:X.shape[0]]
        tsn_features_test=tsn_features[X.shape[0]:tsn_features.shape[0]]     
        
        print tsn_features_train.shape
        print tsn_features_test.shape

        X=np.column_stack((X,tsn_features_train))     
        X_test=np.column_stack((X_test,tsn_features_test)) 

        print X.shape        
        print X_test.shape
        
        pca_features=(np.loadtxt(feature_folder+"dmitry_pca_feats.csv", delimiter=",", skiprows=1, usecols=[1,2]))
        
        dmitry_pca_feats_train=pca_features[:X.shape[0]]
        dmitry_pca_feats_test=pca_features[X.shape[0]:pca_features.shape[0]]     
        
        print dmitry_pca_feats_train.shape
        print dmitry_pca_feats_test.shape

        X=np.column_stack((X,dmitry_pca_feats_train))     
        X_test=np.column_stack((X_test,dmitry_pca_feats_test)) 

        print X.shape        
        print X_test.shape 


        #Create Arrays for meta
        train_stacker=[ 0.0  for k in range (0,(X.shape[0])) ]
        test_stacker=[0.0  for k in range (0,(X_test.shape[0]))]
        
        # CHECK EVerything in five..it could be more efficient     
        
        #create target variable        
        
        #kfolder=StratifiedKFold(y, n_folds=number_of_folds,shuffle=True, random_state=SEED)
        print("kfolder")
        
        #load the 20-fold ids.        
        kfolders=load_ids(input_folder+"5fold_20times.csv")  
        
        printfile(kfolders,"kfolder.pkl")                   
        kfolders=load_datas("kfolder.pkl")
        
        fcount=0
        #number_of_folds=0
        #X,y=shuffle(X,y, random_state=SEED) # Shuffle since the data is ordered by time
        for kfolder in kfolders:
            mean_kapa = 0.0
            i=0 # iterator counter
            print ("starting cross validation with %d kfolds " % (number_of_folds))
            if number_of_folds>0:
                for train_index, test_index in kfolder:
                    # creaning and validation sets
                    X_train, X_cv = X[train_index], X[test_index]
                    y_train, y_cv = np.array(y)[train_index], np.array(y)[test_index]

                    stda=StandardScaler()            
                    X_train=stda.fit_transform(X_train)
                    X_cv=stda.transform(X_cv)                    
    
                    print ("folder %d  train size: %d. test size: %d, cols: %d " % (fcount, (X_train.shape[0]) ,(X_cv.shape[0]) ,(X_train.shape[1]) ))
    
                    
                    preds=bagged_set(X_train,y_train, SEED, 5, X_cv)
                   
                    # compute Loglikelihood metric for this CV fold     
                    kapa = roc_auc_score(y_cv,preds)
                    print "folder %d size train: %d size cv: %d AUC (fold %d/%d): %f" % (fcount,(X_train.shape[0]), (X_cv.shape[0]), i + 1, number_of_folds, kapa)
                    mean_kapa += kapa
                    #save the results
                    no=0
                    for real_index in test_index:
                             train_stacker[real_index]+=(preds[no])
                             keepfold[real_index]=i
                             no+=1
                    i+=1
            fcount+=1
            print "=============================================================================================="
        for u in range(0,len(train_stacker)):
            train_stacker[u]/=float(len(kfolders))
        grand_auc=roc_auc_score(y, train_stacker)
        print (" Grand AUC: %f" % (grand_auc) )
        if (number_of_folds)>0:
            mean_kapa/=number_of_folds
            print (" printing train datasets ")
            printfilcsve(np.column_stack((np.array(idstrain),np.array(train_stacker))), metafolder_train+ outset  + ".train.csv","ID,TARGET")  
            #printfilcsve(np.column_stack((np.array(idstrain),np.array(keepfold))),   "id_fold.csv","ID,FOLD")

        #woe_train, woe_cv= convert_to_woe(np.round(X,2),y, np.round(X_test,2), seed=1, cvals=5, roundings=2, columns=None)

        stda=StandardScaler()            
        X=stda.fit_transform(X)
        X_test=stda.transform(X_test)           
   
        print (" making test predictions ")        
        preds=bagged_set(X, y, SEED, 50, X_test) 
   
        for pr in range (0,len(preds)):            
                    test_stacker[pr]=(preds[pr]) 
    
        preds=np.array(preds)
        printfilcsve(np.column_stack((np.array(ids),np.array(test_stacker))),  metafolder_test+ outset  + ".test.csv","ID,TARGET")                

 
       
       
       



if __name__=="__main__":
  main()
